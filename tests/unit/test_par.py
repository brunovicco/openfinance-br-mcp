"""Unit tests for the PAR (Pushed Authorization Request) client."""

import json
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import respx
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.par import push_authorization_request
from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError

PAR_ENDPOINT = "https://bank.example.com/par"
AUTHZ_ENDPOINT = "https://bank.example.com/authorize"
ISSUER = "https://bank.example.com/"


def _verify_and_decode(token: str, public_key_pem: str, *, audience: str) -> dict:
    """Verifies a JWS token's signature and returns its claims as a dict."""
    public_key = jwk.JWK.from_pem(public_key_pem.encode())
    verified = jwcrypto_jwt.JWT(
        key=public_key, jwt=token, expected_type="JWS", check_claims={"aud": audience}
    )
    claims: dict = json.loads(verified.claims)
    return claims


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "client_id", "test-client-id")
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)
    monkeypatch.setattr(settings, "private_key_kid", "test-kid")


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


class TestPushAuthorizationRequest:
    """Tests for push_authorization_request()."""

    @pytest.mark.asyncio
    async def test_raises_when_client_id_missing(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "client_id", None)
        with pytest.raises(AuthenticationError, match="CLIENT_ID"):
            await push_authorization_request(
                http_client,
                par_endpoint=PAR_ENDPOINT,
                authorization_endpoint=AUTHZ_ENDPOINT,
                issuer=ISSUER,
                scope="accounts",
                pkce=PKCEChallenge.generate(),
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_posts_request_object_and_client_assertion(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        """The PAR POST body must carry a signed JAR 'request' object and
        a private_key_jwt 'client_assertion' - never plain parameters."""
        route = respx.post(PAR_ENDPOINT).mock(
            return_value=httpx.Response(
                201, json={"request_uri": "urn:par:abc123", "expires_in": 60}
            )
        )
        pkce = PKCEChallenge.generate()

        result = await push_authorization_request(
            http_client,
            par_endpoint=PAR_ENDPOINT,
            authorization_endpoint=AUTHZ_ENDPOINT,
            issuer=ISSUER,
            scope="accounts transactions",
            pkce=pkce,
        )

        assert route.call_count == 1
        sent = route.calls[0].request
        form = parse_qs(sent.content.decode())

        assert form["client_id"] == ["test-client-id"]
        assert form["client_assertion_type"] == [
            "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        ]

        request_object = form["request"][0]
        claims = _verify_and_decode(request_object, rsa_public_key_pem, audience=ISSUER)
        assert claims["response_type"] == "code id_token"
        assert claims["client_id"] == "test-client-id"
        assert claims["scope"] == "accounts transactions"
        assert claims["code_challenge"] == pkce.code_challenge
        assert claims["code_challenge_method"] == "S256"

        client_assertion = form["client_assertion"][0]
        assertion_claims = _verify_and_decode(
            client_assertion, rsa_public_key_pem, audience=PAR_ENDPOINT
        )
        assert assertion_claims["iss"] == "test-client-id"

        assert result.state == claims["state"]
        assert result.nonce == claims["nonce"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_redirect_url_with_request_uri(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(PAR_ENDPOINT).mock(
            return_value=httpx.Response(
                201, json={"request_uri": "urn:par:abc123", "expires_in": 60}
            )
        )

        result = await push_authorization_request(
            http_client,
            par_endpoint=PAR_ENDPOINT,
            authorization_endpoint=AUTHZ_ENDPOINT,
            issuer=ISSUER,
            scope="accounts",
            pkce=PKCEChallenge.generate(),
        )

        parsed = urlparse(result.authorization_url)
        assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == AUTHZ_ENDPOINT
        query = parse_qs(parsed.query)
        assert query["client_id"] == ["test-client-id"]
        assert query["request_uri"] == ["urn:par:abc123"]
        assert result.state
        assert result.nonce

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_request_uri_raises(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(PAR_ENDPOINT).mock(return_value=httpx.Response(201, json={}))

        with pytest.raises(AuthenticationError, match="request_uri"):
            await push_authorization_request(
                http_client,
                par_endpoint=PAR_ENDPOINT,
                authorization_endpoint=AUTHZ_ENDPOINT,
                issuer=ISSUER,
                scope="accounts",
                pkce=PKCEChallenge.generate(),
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error_raises_authentication_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(PAR_ENDPOINT).mock(return_value=httpx.Response(400))

        with pytest.raises(AuthenticationError, match="PAR request failed"):
            await push_authorization_request(
                http_client,
                par_endpoint=PAR_ENDPOINT,
                authorization_endpoint=AUTHZ_ENDPOINT,
                issuer=ISSUER,
                scope="accounts",
                pkce=PKCEChallenge.generate(),
            )
