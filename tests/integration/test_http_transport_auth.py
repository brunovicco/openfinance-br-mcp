"""Integration tests for MCP client OAuth 2.1 resource-server auth.

Exercises the real Starlette ASGI app FastMCP builds
(``build_server().streamable_http_app()``) via Starlette's TestClient
(which - unlike a bare ASGITransport - correctly drives the app's
lifespan, starting the session manager's task group the same way a
real ASGI server would). No real network. Covers the structural
guarantees Phase 4 exists for:

  1. The transport enforces RFC 9728 Protected Resource Metadata and
     rejects unauthenticated requests with 401 + WWW-Authenticate.
  2. A valid MCP client token is accepted by the transport layer -
     but that is a completely separate concern from bank
     authentication. See
     test_bank_adapters.py::test_bank_http_calls_never_use_an_mcp_client_token
     for the token-passthrough-impossibility proof.
"""

import time

import httpx
import pytest
import respx
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt
from starlette.testclient import TestClient

from openfinance_br_mcp.config import settings
from openfinance_br_mcp.server import build_server

ISSUER = "https://idp.example.com"
RESOURCE_SERVER = "https://mcp.example.com"
DISCOVERY_URL = f"{ISSUER}/.well-known/openid-configuration"
JWKS_URL = f"{ISSUER}/jwks"


@pytest.fixture
def idp_key() -> jwk.JWK:
    return jwk.JWK.generate(kty="RSA", size=2048, kid="idp-kid-1")


@pytest.fixture(autouse=True)
def _configured_oauth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "mock")
    monkeypatch.setattr(settings, "mcp_oauth_issuer_url", ISSUER)
    monkeypatch.setattr(settings, "mcp_oauth_resource_server_url", RESOURCE_SERVER)


def _make_client_token(signing_key: jwk.JWK) -> str:
    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "aud": RESOURCE_SERVER,
        "sub": "mcp-client-user",
        "client_id": "test-mcp-client",
        "scope": "",
        "iat": now,
        "exp": now + 300,
    }
    token = jwcrypto_jwt.JWT(header={"alg": "PS256", "kid": "idp-kid-1"}, claims=claims)
    token.make_signed_token(signing_key)
    return str(token.serialize())


@pytest.fixture
def http_client() -> TestClient:
    mcp = build_server()
    app = mcp.streamable_http_app()
    with TestClient(app) as client:
        yield client


class TestProtectedResourceMetadata:
    """RFC 9728 Protected Resource Metadata endpoint."""

    def test_well_known_endpoint_returns_valid_metadata(
        self, http_client: TestClient
    ) -> None:
        response = http_client.get("/.well-known/oauth-protected-resource")

        assert response.status_code == 200
        body = response.json()
        assert body["resource"].rstrip("/") == RESOURCE_SERVER
        assert any(
            issuer.rstrip("/") == ISSUER for issuer in body["authorization_servers"]
        )


class TestRequireAuth:
    """The streamable-http endpoint must reject unauthenticated requests."""

    def test_request_without_token_returns_401_with_www_authenticate(
        self, http_client: TestClient
    ) -> None:
        response = http_client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            headers={"Accept": "application/json, text/event-stream"},
        )

        assert response.status_code == 401
        www_authenticate = response.headers.get("www-authenticate", "")
        assert "Bearer" in www_authenticate
        assert "resource_metadata=" in www_authenticate

    @respx.mock
    def test_request_with_valid_token_is_not_rejected_at_the_auth_gate(
        self, idp_key: jwk.JWK, http_client: TestClient
    ) -> None:
        """A valid token must get past RequireAuthMiddleware (any response
        other than 401/403 proves that - what the session manager does
        with the request past that gate is out of scope here)."""
        respx.get(DISCOVERY_URL).mock(
            return_value=httpx.Response(200, json={"jwks_uri": JWKS_URL})
        )
        respx.get(JWKS_URL).mock(
            return_value=httpx.Response(
                200, json={"keys": [dict(idp_key.export_public(as_dict=True))]}
            )
        )
        token = _make_client_token(idp_key)

        response = http_client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json, text/event-stream",
            },
        )

        assert response.status_code not in (401, 403)

    def test_request_with_garbage_token_still_returns_401(
        self, http_client: TestClient
    ) -> None:
        response = http_client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            headers={
                "Authorization": "Bearer not-a-real-token",
                "Accept": "application/json, text/event-stream",
            },
        )

        assert response.status_code == 401
