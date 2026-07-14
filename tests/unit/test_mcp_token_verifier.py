"""Unit tests for JWTTokenVerifier (MCP client resource-server auth).

Uses a real RSA key pair (jwcrypto) to sign test tokens - genuine
sign/verify round-trips, not mocked crypto - against a respx-mocked
issuer discovery document + JWKS endpoint.
"""

import time

import httpx
import pytest
import respx
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.mcp_token_verifier import JWTTokenVerifier
from openfinance_br_mcp.auth.mtls_binding import client_cert_thumbprint

ISSUER = "https://idp.example.com"
RESOURCE_SERVER = "https://mcp.example.com"
DISCOVERY_URL = f"{ISSUER}/.well-known/openid-configuration"
JWKS_URL = f"{ISSUER}/jwks"


@pytest.fixture
def idp_key() -> jwk.JWK:
    """A throwaway RSA key standing in for the IdP's signing key."""
    return jwk.JWK.generate(kty="RSA", size=2048, kid="idp-kid-1")


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


def _mock_discovery_and_jwks(idp_key: jwk.JWK) -> None:
    respx.get(DISCOVERY_URL).mock(
        return_value=httpx.Response(200, json={"jwks_uri": JWKS_URL})
    )
    respx.get(JWKS_URL).mock(
        return_value=httpx.Response(
            200, json={"keys": [dict(idp_key.export_public(as_dict=True))]}
        )
    )


def _make_token(
    signing_key: jwk.JWK,
    *,
    iss: str = ISSUER,
    aud: str = RESOURCE_SERVER,
    kid: str = "idp-kid-1",
    scope: str = "accounts:read",
    exp_delta: int = 300,
    sub: str = "user-123",
    client_id: str = "test-mcp-client",
    cnf_thumbprint: str | None = None,
) -> str:
    now = int(time.time())
    claims = {
        "iss": iss,
        "aud": aud,
        "sub": sub,
        "client_id": client_id,
        "scope": scope,
        "iat": now,
        "exp": now + exp_delta,
    }
    if cnf_thumbprint is not None:
        claims["cnf"] = {"x5t#S256": cnf_thumbprint}
    token = jwcrypto_jwt.JWT(header={"alg": "PS256", "kid": kid}, claims=claims)
    token.make_signed_token(signing_key)
    return str(token.serialize())


class TestVerifyToken:
    """Tests for JWTTokenVerifier.verify_token()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_access_token_for_valid_jwt(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key)

        result = await verifier.verify_token(token)

        assert result is not None
        assert result.subject == "user-123"
        assert result.client_id == "test-mcp-client"
        assert result.scopes == ["accounts:read"]
        assert result.resource == RESOURCE_SERVER

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_none_for_wrong_signature(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        forged_key = jwk.JWK.generate(kty="RSA", size=2048, kid="idp-kid-1")
        token = _make_token(forged_key)

        result = await verifier.verify_token(token)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_none_for_wrong_audience(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        """This is the audience-binding check (RFC 8707) that makes token
        passthrough structurally rejectable: a token minted for some
        other resource server must not verify here."""
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key, aud="https://some-other-server.example.com")

        result = await verifier.verify_token(token)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_none_for_wrong_issuer(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key, iss="https://impostor-idp.example.com")

        result = await verifier.verify_token(token)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_none_for_expired_token(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key, exp_delta=-3600)

        result = await verifier.verify_token(token)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_none_when_kid_not_in_jwks(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key, kid="unknown-kid")

        result = await verifier.verify_token(token)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_garbage_token(
        self, http_client: httpx.AsyncClient
    ) -> None:
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )

        result = await verifier.verify_token("not-a-jwt-at-all")

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_jwks_is_cached_across_calls(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        respx.get(DISCOVERY_URL).mock(
            return_value=httpx.Response(200, json={"jwks_uri": JWKS_URL})
        )
        jwks_route = respx.get(JWKS_URL).mock(
            return_value=httpx.Response(
                200, json={"keys": [dict(idp_key.export_public(as_dict=True))]}
            )
        )
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key)

        await verifier.verify_token(token)
        await verifier.verify_token(token)

        assert jwks_route.call_count == 1


class TestMTLSCertificateBinding:
    """Tests for RFC 8705 'cnf.x5t#S256' certificate-bound token checks."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_accepts_token_when_thumbprint_matches_current_connection(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key, cnf_thumbprint="abc123thumbprint")
        reset_token = client_cert_thumbprint.set("abc123thumbprint")
        try:
            result = await verifier.verify_token(token)
        finally:
            client_cert_thumbprint.reset(reset_token)

        assert result is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_rejects_token_when_thumbprint_mismatches(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key, cnf_thumbprint="abc123thumbprint")
        reset_token = client_cert_thumbprint.set("some-other-thumbprint")
        try:
            result = await verifier.verify_token(token)
        finally:
            client_cert_thumbprint.reset(reset_token)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_rejects_bound_token_when_no_client_cert_present(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        """A stolen cert-bound bearer token replayed without mTLS must fail."""
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client, issuer_url=ISSUER, resource_server_url=RESOURCE_SERVER
        )
        token = _make_token(idp_key, cnf_thumbprint="abc123thumbprint")

        result = await verifier.verify_token(token)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_accepts_unbound_token_when_binding_not_required(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client,
            issuer_url=ISSUER,
            resource_server_url=RESOURCE_SERVER,
            require_mtls_binding=False,
        )
        token = _make_token(idp_key)

        result = await verifier.verify_token(token)

        assert result is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_rejects_unbound_token_when_binding_required(
        self, idp_key: jwk.JWK, http_client: httpx.AsyncClient
    ) -> None:
        """require_mtls_binding=True closes the downgrade path where an
        attacker simply requests/replays a token with no 'cnf' claim."""
        _mock_discovery_and_jwks(idp_key)
        verifier = JWTTokenVerifier(
            http_client,
            issuer_url=ISSUER,
            resource_server_url=RESOURCE_SERVER,
            require_mtls_binding=True,
        )
        token = _make_token(idp_key)

        result = await verifier.verify_token(token)

        assert result is None
