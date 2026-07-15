"""Unit tests for the consent flow MCP tools (tools/consent.py).

Exercises the full orchestration (directory resolution, client
credentials, consent creation, PAR/JAR, and - for complete_consent -
authorization code exchange and ID token verification) against a
respx-mocked bank, using a real RSA key pair on both the client and
bank side so the JOSE round-trips are genuine, not mocked away.
"""

import inspect
import json
import time
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import respx
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.authorization_session import (
    AuthorizationSessionStore,
    PendingAuthorization,
)
from openfinance_br_mcp.auth.consent import ConsentManager
from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.auth.token import TokenStore
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.context import AppContext
from openfinance_br_mcp.directory.client import DirectoryClient
from openfinance_br_mcp.exceptions import (
    ConsentDeniedError,
    ConsentError,
    ValidationError,
)
from openfinance_br_mcp.tools.consent import (
    check_consent_status,
    complete_consent,
    revoke_consent,
    start_consent,
)

DIRECTORY_BASE = "https://data.directory.openbankingbrasil.org.br"
ISSUER = "https://bank.example.com/api/pub/"
TOKEN_ENDPOINT = "https://bank.example.com/api/pub/token"  # noqa: S105
PAR_ENDPOINT = "https://bank.example.com/api/pub/par"
AUTHZ_ENDPOINT = "https://bank.example.com/api/pub/authorize"
JWKS_URL = "https://bank.example.com/api/pub/jwks"
DISCOVERY_URL = "https://bank.example.com/api/pub/.well-known/openid-configuration"
CONSENTS_BASE = "https://bank.example.com/open-banking"
SUBJECT_ID = "12345678900"


def _nubank_organisation() -> dict:
    return {
        "OrganisationId": "org-1",
        "OrganisationName": "NU PAGAMENTOS S.A.",
        "RegistrationId": "18236120",
        "Status": "Active",
        "AuthorisationServers": [
            {
                "AuthorisationServerId": "as-1",
                "Issuer": ISSUER,
                "OpenIDDiscoveryDocument": DISCOVERY_URL,
                "PayloadSigningCertLocationUri": JWKS_URL,
                "Status": "Active",
                "ApiResources": [
                    {
                        "ApiResourceId": "res-1",
                        "ApiVersion": "3.3.1",
                        "ApiFamilyType": "consents",
                        "Status": "Active",
                        "ApiDiscoveryEndpoints": [
                            {"ApiEndpoint": f"{CONSENTS_BASE}/consents/v3/consents"}
                        ],
                    }
                ],
            }
        ],
    }


def _mock_directory_and_discovery() -> None:
    respx.get(f"{DIRECTORY_BASE}/participants").mock(
        return_value=httpx.Response(200, json=[_nubank_organisation()])
    )
    respx.get(DISCOVERY_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "issuer": ISSUER,
                "token_endpoint": TOKEN_ENDPOINT,
                "authorization_endpoint": AUTHZ_ENDPOINT,
                "pushed_authorization_request_endpoint": PAR_ENDPOINT,
            },
        )
    )


def _fake_ctx(app_context: AppContext) -> SimpleNamespace:
    return SimpleNamespace(
        request_context=SimpleNamespace(lifespan_context=app_context),
        elicit_url=AsyncMock(),
    )


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "environment", "sandbox")
    monkeypatch.setattr(settings, "client_id", "test-client-id")
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)


def _app(
    http_client: httpx.AsyncClient, *, directory: DirectoryClient | None
) -> AppContext:
    return AppContext(
        http_client=http_client,
        token_store=TokenStore(),
        adapters={},
        categorizer=AsyncMock(),
        consent_manager=ConsentManager(http_client),
        authorization_sessions=AuthorizationSessionStore(),
        principal_bindings=AsyncMock(),
        payment_consent_manager=AsyncMock(),
        idempotency_store=AsyncMock(),
        directory=directory,
    )


class TestStartConsentMockMode:
    """start_consent must refuse to run in mock mode."""

    @pytest.mark.asyncio
    async def test_raises_in_mock_mode(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "environment", "mock")
        app = _app(http_client, directory=None)

        with pytest.raises(ValidationError, match="not applicable in mock mode"):
            await inspect.unwrap(start_consent)(
                SUBJECT_ID, "nubank", ["accounts"], _fake_ctx(app)
            )


class TestStartConsent:
    """Tests for start_consent()'s end-to-end orchestration."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_creates_consent_and_returns_par_authorization_url(
        self, http_client: httpx.AsyncClient
    ) -> None:
        _mock_directory_and_discovery()
        respx.post(TOKEN_ENDPOINT).mock(
            return_value=httpx.Response(
                200, json={"access_token": "cc-token", "expires_in": 300}
            )
        )
        respx.post(f"{CONSENTS_BASE}/consents/v3/consents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": {
                        "consentId": "urn:bank:C1",
                        "status": "AWAITING_AUTHORISATION",
                    }
                },
            )
        )
        par_route = respx.post(PAR_ENDPOINT).mock(
            return_value=httpx.Response(
                201, json={"request_uri": "urn:par:xyz", "expires_in": 60}
            )
        )
        directory = DirectoryClient(http_client, base_url=DIRECTORY_BASE)
        app = _app(http_client, directory=directory)
        ctx = _fake_ctx(app)

        result = await inspect.unwrap(start_consent)(
            SUBJECT_ID,
            "nubank",
            ["accounts", "transactions"],
            ctx,
            request_url_elicitation=True,
        )

        assert result.consent_id == "urn:bank:C1"
        parsed = urlparse(result.authorization_url)
        assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == AUTHZ_ENDPOINT
        query = parse_qs(parsed.query)
        assert query["request_uri"] == ["urn:par:xyz"]
        ctx.elicit_url.assert_awaited_once()
        assert ctx.elicit_url.await_args.kwargs["url"] == result.authorization_url

        # The PAR request must embed the consent in its 'scope' claim,
        # per the FAPI-BR 'consent:<id>' convention.
        par_form = parse_qs(par_route.calls[0].request.content.decode())
        request_object = par_form["request"][0]
        header_and_claims = jwcrypto_jwt.JWT(jwt=request_object)
        claims = json.loads(header_and_claims.token.objects["payload"])
        assert "consent:urn:bank:C1" in claims["scope"]

        # A pending authorization session must now exist, keyed by the
        # state embedded in that same request object. pop() raises if
        # missing, so a successful pop is itself the existence check.
        session = await app.authorization_sessions.pop(claims["state"])
        assert session.consent_id == "urn:bank:C1"


class TestCompleteConsent:
    """Tests for complete_consent()'s callback handling."""

    @pytest.mark.asyncio
    async def test_raises_when_bank_denies_authorization(
        self, http_client: httpx.AsyncClient
    ) -> None:
        app = _app(http_client, directory=None)
        callback = (
            "https://localhost:8080/callback"
            "#error=access_denied&error_description=user+declined"
        )

        with pytest.raises(ConsentDeniedError, match="access_denied"):
            await inspect.unwrap(complete_consent)(callback, _fake_ctx(app))

    @pytest.mark.asyncio
    async def test_raises_when_code_or_state_missing(
        self, http_client: httpx.AsyncClient
    ) -> None:
        app = _app(http_client, directory=None)
        callback = "https://localhost:8080/callback#state=abc"

        with pytest.raises(ValidationError, match="INVALID_CALLBACK_URL|code"):
            await inspect.unwrap(complete_consent)(callback, _fake_ctx(app))

    @pytest.mark.asyncio
    async def test_raises_when_state_unknown(
        self, http_client: httpx.AsyncClient
    ) -> None:
        app = _app(http_client, directory=None)
        callback = "https://localhost:8080/callback#code=abc&state=never-issued"

        with pytest.raises(ConsentError, match="No pending authorization"):
            await inspect.unwrap(complete_consent)(callback, _fake_ctx(app))

    @pytest.mark.asyncio
    @respx.mock
    async def test_exchanges_code_verifies_id_token_and_returns_status(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        bank_key = jwk.JWK.generate(kty="RSA", size=2048, kid="bank-kid-1")
        jwks = {"keys": [dict(bank_key.export_public(as_dict=True))]}
        respx.get(JWKS_URL).mock(return_value=httpx.Response(200, json=jwks))
        respx.post(TOKEN_ENDPOINT).mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "consent-bound-token",
                    "refresh_token": "rt",
                    "expires_in": 900,
                },
            )
        )
        respx.get(f"{CONSENTS_BASE}/consents/v3/consents/urn:bank:C1").mock(
            return_value=httpx.Response(
                200, json={"data": {"consentId": "urn:bank:C1", "status": "AUTHORISED"}}
            )
        )

        directory = DirectoryClient(http_client, base_url=DIRECTORY_BASE)
        app = _app(http_client, directory=directory)
        pkce = PKCEChallenge.generate()
        await app.authorization_sessions.save(
            "the-state",
            PendingAuthorization(
                bank_id="nubank",
                bank_base_url=CONSENTS_BASE,
                consent_id="urn:bank:C1",
                subject_id=SUBJECT_ID,
                pkce=pkce,
                nonce="the-nonce",
                issuer=ISSUER,
                token_endpoint=TOKEN_ENDPOINT,
                created_at=datetime.now(UTC),
            ),
        )
        # Seed the consent manager's cache so get_status() finds it -
        # it was created by start_consent in the real flow.
        await app.consent_manager._set_cached(
            "nubank",
            SUBJECT_ID,
            {
                "data": {
                    "consentId": "urn:bank:C1",
                    "status": "AWAITING_AUTHORISATION",
                },
                "scopes": ["accounts"],
            },
        )

        now = int(time.time())
        inner = jwcrypto_jwt.JWT(
            header={"alg": "PS256", "kid": "bank-kid-1"},
            claims={
                "iss": ISSUER,
                "sub": SUBJECT_ID,
                "aud": "test-client-id",
                "nonce": "the-nonce",
                "acr": "urn:brasil:openbanking:loa2",
                "iat": now,
                "exp": now + 300,
            },
        )
        inner.make_signed_token(bank_key)
        client_public_key = jwk.JWK.from_pem(rsa_public_key_pem.encode())
        outer = jwcrypto_jwt.JWT(
            header={"alg": "RSA-OAEP", "enc": "A256GCM", "cty": "JWT"},
            claims=inner.serialize(),
        )
        outer.make_encrypted_token(client_public_key)
        id_token = outer.serialize()

        callback = (
            "https://localhost:8080/callback"
            f"#code=auth-code-123&state=the-state&id_token={id_token}"
        )

        result = await inspect.unwrap(complete_consent)(callback, _fake_ctx(app))

        assert result.consent_id == "urn:bank:C1"
        assert result.status == "AUTHORISED"
        saved = await app.token_store.get_valid_token(
            "nubank", SUBJECT_ID, app.http_client, TOKEN_ENDPOINT
        )
        assert saved.access_token == "consent-bound-token"  # noqa: S105

        # The session must be single-use.
        with pytest.raises(ConsentError, match="No pending authorization"):
            await app.authorization_sessions.pop("the-state")


class TestCheckAndRevokeWithoutSession:
    """check_consent_status/revoke_consent must fail clearly with no prior session."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_status_raises_without_session(
        self, http_client: httpx.AsyncClient
    ) -> None:
        _mock_directory_and_discovery()
        directory = DirectoryClient(http_client, base_url=DIRECTORY_BASE)
        app = _app(http_client, directory=directory)

        with pytest.raises(ConsentError, match="No active consent session"):
            await inspect.unwrap(check_consent_status)(
                SUBJECT_ID, "nubank", _fake_ctx(app)
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_revoke_raises_without_session(
        self, http_client: httpx.AsyncClient
    ) -> None:
        _mock_directory_and_discovery()
        directory = DirectoryClient(http_client, base_url=DIRECTORY_BASE)
        app = _app(http_client, directory=directory)

        with pytest.raises(ConsentError, match="No active consent session"):
            await inspect.unwrap(revoke_consent)(SUBJECT_ID, "nubank", _fake_ctx(app))
