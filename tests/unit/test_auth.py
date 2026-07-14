"""Unit tests for the authentication modules.

Covers PKCE (generation and verification) and TokenStore (storage,
idempotent refresh, and token revocation).
"""

import asyncio
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.auth.token import TokenResponse, TokenStore
from openfinance_br_mcp.config import settings


class TestPKCEChallenge:
    """Tests for PKCE generation and verification."""

    def test_generate_returns_valid_challenge(self) -> None:
        """PKCEChallenge.generate() should return a valid verifier/challenge."""
        challenge = PKCEChallenge.generate()

        assert len(challenge.code_verifier) >= 43
        assert len(challenge.code_verifier) <= 128
        assert challenge.code_challenge_method == "S256"
        assert len(challenge.code_challenge) > 0

    def test_generate_is_unique_each_call(self) -> None:
        """Each call to generate() should produce a different pair."""
        c1 = PKCEChallenge.generate()
        c2 = PKCEChallenge.generate()

        assert c1.code_verifier != c2.code_verifier
        assert c1.code_challenge != c2.code_challenge

    def test_verify_correct_verifier(self) -> None:
        """verify() should return True for the correct verifier."""
        challenge = PKCEChallenge.generate()
        assert challenge.verify(challenge.code_verifier) is True

    def test_verify_wrong_verifier(self) -> None:
        """verify() should return False for any other verifier."""
        challenge = PKCEChallenge.generate()
        other = PKCEChallenge.generate()
        assert challenge.verify(other.code_verifier) is False

    def test_challenge_is_base64url_no_padding(self) -> None:
        """code_challenge should not contain '=' (base64 padding)."""
        challenge = PKCEChallenge.generate()
        assert "=" not in challenge.code_challenge
        assert "=" not in challenge.code_verifier


class TestTokenResponse:
    """Tests for TokenResponse and expiration detection."""

    def test_is_expired_when_past_expiry(self) -> None:
        """is_expired() should return True for an expired token."""
        token = TokenResponse(
            {
                "access_token": "tok",
                "expires_in": 60,
                "_obtained_at": datetime.now(UTC) - timedelta(seconds=120),
            }
        )
        assert token.is_expired() is True

    def test_is_not_expired_when_fresh(self) -> None:
        """is_expired() should return False for a freshly obtained token."""
        token = TokenResponse(
            {
                "access_token": "tok",
                "expires_in": 3600,
                "_obtained_at": datetime.now(UTC),
            }
        )
        assert token.is_expired() is False

    def test_buffer_seconds_triggers_early_refresh(self) -> None:
        """A token within the buffer window should be considered expired."""
        token = TokenResponse(
            {
                "access_token": "tok",
                "expires_in": 90,  # expires in 90s
                "_obtained_at": datetime.now(UTC) - timedelta(seconds=40),
                # With buffer=60: 90-60=30s of real validity; 40s
                # elapsed > 30s → expired
            }
        )
        assert token.is_expired(buffer_seconds=60) is True


class TestTokenStore:
    """Tests for TokenStore, focused on concurrency and idempotency."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_valid_token(
        self, valid_token: TokenResponse
    ) -> None:
        """A saved token should be retrievable without a refresh if still valid."""
        store = TokenStore()
        await store.save("nubank", "user1", valid_token)

        import httpx

        http = httpx.AsyncClient()
        result = await store.get_valid_token(
            "nubank", "user1", http, "https://token.example.com"
        )

        assert result.access_token == valid_token.access_token

    @pytest.mark.asyncio
    async def test_same_subject_different_banks_do_not_collide(
        self, valid_token: TokenResponse
    ) -> None:
        """Regression test (P0.1): a subject_id authorized at two banks
        must not have one bank's token overwrite the other's."""
        store = TokenStore()
        other_token = TokenResponse({**valid_token, "access_token": "other-bank-token"})
        await store.save("nubank", "user1", valid_token)
        await store.save("itau", "user1", other_token)

        import httpx

        http = httpx.AsyncClient()
        nubank_result = await store.get_valid_token(
            "nubank", "user1", http, "https://nubank.example.com"
        )
        itau_result = await store.get_valid_token(
            "itau", "user1", http, "https://itau.example.com"
        )

        assert nubank_result.access_token == valid_token.access_token
        assert itau_result.access_token == "other-bank-token"  # noqa: S105

    @pytest.mark.asyncio
    async def test_concurrent_refresh_is_idempotent(
        self, valid_token: TokenResponse
    ) -> None:
        """Multiple concurrent tasks should not trigger multiple refreshes."""
        store = TokenStore()
        expired_token = TokenResponse(
            {
                **valid_token,
                "expires_in": 1,
                "_obtained_at": datetime.now(UTC) - timedelta(seconds=10),
            }
        )
        await store.save("nubank", "user2", expired_token)

        refresh_count = 0

        async def fake_refresh(*args, **kwargs):
            nonlocal refresh_count
            refresh_count += 1
            await asyncio.sleep(0.01)
            return TokenResponse(
                {
                    "access_token": "new_token",
                    "expires_in": 3600,
                    "_obtained_at": datetime.now(UTC),
                }
            )

        import unittest.mock as mock

        with mock.patch.object(store, "_refresh", side_effect=fake_refresh):
            import httpx

            http = httpx.AsyncClient()
            tasks = [
                store.get_valid_token("nubank", "user2", http, "https://x.com")
                for _ in range(5)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

        assert refresh_count == 1, f"Expected 1 refresh, got {refresh_count}"

    @pytest.mark.asyncio
    async def test_revoke_removes_token(self, valid_token: TokenResponse) -> None:
        """revoke() should remove the token from the store."""
        store = TokenStore()
        await store.save("nubank", "user3", valid_token)
        await store.revoke("nubank", "user3")

        with pytest.raises(KeyError):
            await store.get_valid_token(
                "nubank", "user3", httpx.AsyncClient(), "https://x.com"
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_refresh_authenticates_via_private_key_jwt(
        self, monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
    ) -> None:
        """_refresh() must authenticate with private_key_jwt (RFC 7523),
        not a plain client_id form field - the only method FAPI-BR
        2.2.0 accepts at the token endpoint."""
        monkeypatch.setattr(settings, "client_id", "test-client-id")
        monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)
        token_endpoint = "https://bank.example.com/token"  # noqa: S105
        route = respx.post(token_endpoint).mock(
            return_value=httpx.Response(
                200, json={"access_token": "new_token", "expires_in": 3600}
            )
        )
        store = TokenStore()
        expiring = TokenResponse(
            {
                "access_token": "old_token",
                "refresh_token": "refresh_abc",
                "expires_in": 1,
                "_obtained_at": datetime.now(UTC) - timedelta(seconds=10),
            }
        )

        refreshed = await store._refresh(expiring, httpx.AsyncClient(), token_endpoint)

        assert refreshed.access_token == "new_token"  # noqa: S105
        sent_form = parse_qs(route.calls[0].request.content.decode())
        assert sent_form["grant_type"] == ["refresh_token"]
        assert sent_form["client_assertion_type"] == [
            "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        ]
        assert "client_assertion" in sent_form
