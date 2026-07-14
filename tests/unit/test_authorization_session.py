"""Unit tests for AuthorizationSessionStore."""

from datetime import UTC, datetime, timedelta

import pytest

from openfinance_br_mcp.auth.authorization_session import (
    AuthorizationSessionStore,
    PendingAuthorization,
)
from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.exceptions import ConsentError


def _session(created_at: datetime | None = None) -> PendingAuthorization:
    return PendingAuthorization(
        bank_id="nubank",
        bank_base_url="https://bank.example.com/open-banking",
        consent_id="urn:bank:C1",
        subject_id="12345678900",
        pkce=PKCEChallenge.generate(),
        nonce="test-nonce",
        issuer="https://bank.example.com/",
        token_endpoint="https://bank.example.com/token",  # noqa: S106
        created_at=created_at or datetime.now(UTC),
    )


@pytest.mark.asyncio
class TestAuthorizationSessionStore:
    """Tests for AuthorizationSessionStore.

    Backed by a KeyValueStore (see auth/store_protocol.py) - pop()
    returns a session reconstructed from JSON, not the original
    object, so assertions compare by value (==), not identity (is).
    """

    async def test_save_and_pop_returns_the_session(self) -> None:
        store = AuthorizationSessionStore()
        session = _session()

        await store.save("state-1", session)

        assert await store.pop("state-1") == session

    async def test_pop_is_single_use(self) -> None:
        store = AuthorizationSessionStore()
        await store.save("state-1", _session())
        await store.pop("state-1")

        with pytest.raises(ConsentError, match="No pending authorization"):
            await store.pop("state-1")

    async def test_pop_unknown_state_raises(self) -> None:
        store = AuthorizationSessionStore()
        with pytest.raises(ConsentError, match="No pending authorization"):
            await store.pop("unknown-state")

    async def test_expired_session_is_pruned(self) -> None:
        store = AuthorizationSessionStore()
        old_session = _session(created_at=datetime.now(UTC) - timedelta(minutes=20))
        await store.save("state-1", old_session)

        with pytest.raises(ConsentError, match="No pending authorization"):
            await store.pop("state-1")

    async def test_fresh_session_survives_pruning_of_others(self) -> None:
        store = AuthorizationSessionStore()
        old_session = _session(created_at=datetime.now(UTC) - timedelta(minutes=20))
        fresh_session = _session()
        await store.save("state-old", old_session)
        await store.save("state-fresh", fresh_session)

        assert await store.pop("state-fresh") == fresh_session
        with pytest.raises(ConsentError, match="No pending authorization"):
            await store.pop("state-old")
