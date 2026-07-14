"""Unit tests for auth/store_protocol.py::InMemoryStore."""

import pytest

from openfinance_br_mcp.auth.store_protocol import InMemoryStore


class TestInMemoryStore:
    """Tests for InMemoryStore."""

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing_key(self) -> None:
        store = InMemoryStore()

        assert await store.get("missing") is None

    @pytest.mark.asyncio
    async def test_set_then_get_returns_the_value(self) -> None:
        store = InMemoryStore()

        await store.set("key1", "value1")

        assert await store.get("key1") == "value1"

    @pytest.mark.asyncio
    async def test_set_overwrites_existing_value(self) -> None:
        store = InMemoryStore()

        await store.set("key1", "first")
        await store.set("key1", "second")

        assert await store.get("key1") == "second"

    @pytest.mark.asyncio
    async def test_ttl_is_accepted_but_ignored(self) -> None:
        """InMemoryStore never expires entries itself (see class docstring)
        - callers relying on TTL semantics (e.g. TokenResponse.is_expired())
        must check expiry themselves."""
        store = InMemoryStore()

        await store.set("key1", "value1", ttl_seconds=1)

        assert await store.get("key1") == "value1"

    @pytest.mark.asyncio
    async def test_delete_removes_the_key(self) -> None:
        store = InMemoryStore()
        await store.set("key1", "value1")

        await store.delete("key1")

        assert await store.get("key1") is None

    @pytest.mark.asyncio
    async def test_delete_is_a_noop_for_missing_key(self) -> None:
        store = InMemoryStore()

        await store.delete("never-existed")  # must not raise
