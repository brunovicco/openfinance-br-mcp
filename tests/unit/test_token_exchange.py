"""Unit tests for token endpoint grant exchanges."""

from urllib.parse import parse_qs

import httpx
import pytest
import respx

from openfinance_br_mcp.auth.token_exchange import (
    exchange_authorization_code,
    exchange_client_credentials,
)
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError

TOKEN_ENDPOINT = "https://bank.example.com/token"  # noqa: S105


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "client_id", "test-client-id")
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


class TestExchangeClientCredentials:
    """Tests for exchange_client_credentials()."""

    @pytest.mark.asyncio
    async def test_raises_when_client_id_missing(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "client_id", None)
        with pytest.raises(AuthenticationError, match="CLIENT_ID"):
            await exchange_client_credentials(
                http_client, token_endpoint=TOKEN_ENDPOINT, scope="consents"
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_posts_client_credentials_grant_with_private_key_jwt(
        self, http_client: httpx.AsyncClient
    ) -> None:
        route = respx.post(TOKEN_ENDPOINT).mock(
            return_value=httpx.Response(
                200, json={"access_token": "cc_token", "expires_in": 300}
            )
        )

        token = await exchange_client_credentials(
            http_client, token_endpoint=TOKEN_ENDPOINT, scope="consents"
        )

        assert token.access_token == "cc_token"  # noqa: S105
        form = parse_qs(route.calls[0].request.content.decode())
        assert form["grant_type"] == ["client_credentials"]
        assert form["scope"] == ["consents"]
        assert form["client_assertion_type"] == [
            "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        ]
        assert "client_assertion" in form

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error_raises_authentication_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(TOKEN_ENDPOINT).mock(return_value=httpx.Response(400))

        with pytest.raises(AuthenticationError, match="Token request failed"):
            await exchange_client_credentials(
                http_client, token_endpoint=TOKEN_ENDPOINT, scope="consents"
            )


class TestExchangeAuthorizationCode:
    """Tests for exchange_authorization_code()."""

    @pytest.mark.asyncio
    async def test_raises_when_client_id_missing(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "client_id", None)
        with pytest.raises(AuthenticationError, match="CLIENT_ID"):
            await exchange_authorization_code(
                http_client,
                token_endpoint=TOKEN_ENDPOINT,
                code="abc123",
                code_verifier="verifier",
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_posts_authorization_code_grant_with_pkce_and_private_key_jwt(
        self, http_client: httpx.AsyncClient
    ) -> None:
        route = respx.post(TOKEN_ENDPOINT).mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "ac_token",
                    "refresh_token": "rt_token",
                    "expires_in": 900,
                },
            )
        )

        token = await exchange_authorization_code(
            http_client,
            token_endpoint=TOKEN_ENDPOINT,
            code="abc123",
            code_verifier="the-verifier",
        )

        assert token.access_token == "ac_token"  # noqa: S105
        assert token.refresh_token == "rt_token"  # noqa: S105
        form = parse_qs(route.calls[0].request.content.decode())
        assert form["grant_type"] == ["authorization_code"]
        assert form["code"] == ["abc123"]
        assert form["code_verifier"] == ["the-verifier"]
        assert form["redirect_uri"] == [str(settings.redirect_uri)]
        assert "client_assertion" in form

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error_raises_authentication_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(TOKEN_ENDPOINT).mock(return_value=httpx.Response(400))

        with pytest.raises(AuthenticationError, match="Token request failed"):
            await exchange_authorization_code(
                http_client,
                token_endpoint=TOKEN_ENDPOINT,
                code="abc123",
                code_verifier="verifier",
            )
