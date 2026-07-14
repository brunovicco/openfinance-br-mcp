"""Integration tests for auth/redis_backend.py against a real Redis.

Uses a real local Redis instance rather than mocking the client -
this module exists specifically to prove state is shared across
independent processes, which a mock can't demonstrate. Skips
gracefully if no Redis is reachable (e.g. CI without one running).

Start one for local dev with, e.g.:
    redis-server --port 6399 --daemonize yes --save "" --appendonly no
"""

import asyncio
import uuid

import pytest
import redis.asyncio as redis_asyncio

from openfinance_br_mcp.auth.redis_backend import RedisStore
from openfinance_br_mcp.auth.token import TokenResponse, TokenStore

REDIS_TEST_URL = "redis://localhost:6399/0"


async def _redis_reachable() -> bool:
    try:
        client = redis_asyncio.from_url(REDIS_TEST_URL)
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False


@pytest.fixture(autouse=True)
async def _skip_without_redis() -> None:
    if not await _redis_reachable():
        pytest.skip(f"No Redis reachable at {REDIS_TEST_URL} - start one to run this")


@pytest.fixture
def key() -> str:
    """A unique key per test, so tests don't interfere via shared state."""
    return f"test:{uuid.uuid4()}"


class TestRedisStore:
    """Tests for RedisStore against a real Redis."""

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing_key(self, key: str) -> None:
        store = RedisStore(REDIS_TEST_URL)
        try:
            assert await store.get(key) is None
        finally:
            await store.aclose()

    @pytest.mark.asyncio
    async def test_set_then_get_returns_the_value(self, key: str) -> None:
        store = RedisStore(REDIS_TEST_URL)
        try:
            await store.set(key, "hello")
            assert await store.get(key) == "hello"
        finally:
            await store.delete(key)
            await store.aclose()

    @pytest.mark.asyncio
    async def test_delete_removes_the_key(self, key: str) -> None:
        store = RedisStore(REDIS_TEST_URL)
        try:
            await store.set(key, "hello")
            await store.delete(key)
            assert await store.get(key) is None
        finally:
            await store.aclose()

    @pytest.mark.asyncio
    async def test_ttl_expires_the_value(self, key: str) -> None:
        store = RedisStore(REDIS_TEST_URL)
        try:
            await store.set(key, "hello", ttl_seconds=1)
            assert await store.get(key) == "hello"
            await asyncio.sleep(1.5)
            assert await store.get(key) is None
        finally:
            await store.aclose()

    @pytest.mark.asyncio
    async def test_two_independent_store_instances_share_state(self, key: str) -> None:
        """Simulates two Kubernetes replicas: two separate RedisStore
        instances (separate connections, no shared Python objects)
        pointed at the same Redis must see each other's writes."""
        store_a = RedisStore(REDIS_TEST_URL)
        store_b = RedisStore(REDIS_TEST_URL)
        try:
            await store_a.set(key, "written-by-replica-a")

            assert await store_b.get(key) == "written-by-replica-a"
        finally:
            await store_a.delete(key)
            await store_a.aclose()
            await store_b.aclose()


class TestTokenStoreAcrossReplicas:
    """The plan's own verification criterion: a token saved by one
    TokenStore instance ('replica') must be visible to another,
    when both share a RedisStore backend."""

    @pytest.mark.asyncio
    async def test_token_saved_by_one_replica_is_visible_to_another(self) -> None:
        subject_id = f"user-{uuid.uuid4()}"
        store_a = RedisStore(REDIS_TEST_URL)
        store_b = RedisStore(REDIS_TEST_URL)
        replica_a = TokenStore(store=store_a)
        replica_b = TokenStore(store=store_b)

        try:
            token = TokenResponse(
                {"access_token": "shared-across-replicas", "expires_in": 3600}
            )
            await replica_a.save(subject_id, token)

            import httpx

            seen_by_b = await replica_b.get_valid_token(
                subject_id, httpx.AsyncClient(), "https://unused.example.com/token"
            )

            assert seen_by_b.access_token == "shared-across-replicas"  # noqa: S105
        finally:
            await replica_a.revoke(subject_id)
            await store_a.aclose()
            await store_b.aclose()
