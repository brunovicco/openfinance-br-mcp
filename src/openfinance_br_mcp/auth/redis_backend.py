"""Redis-backed KeyValueStore for multi-replica deployments.

Implements auth/store_protocol.py::KeyValueStore against
``redis.asyncio``, so a token or consent saved by one Kubernetes
replica (see k8s/deployment.yaml's ``replicas: 2``) is visible to
every other replica sharing the same Redis instance
(k8s/config-and-secrets.yaml's ``REDIS_URL``).

``lock()`` is a real distributed lock (``redis.asyncio.lock.Lock``,
SET NX + TTL under the hood), so TokenStore's refresh idempotency
(auth/token.py) holds across replicas, not just within one process.

Example:
    >>> store = RedisStore("redis://redis.fintech.svc.cluster.local:6379/0")
    >>> await store.set("token:user123", '{"access_token": "..."}', ttl_seconds=900)
    >>> async with store.lock("token:user123"):
    ...     ...  # mutually exclusive across every replica sharing this Redis
"""

from contextlib import AbstractAsyncContextManager

import redis.asyncio as redis


class RedisStore:
    """KeyValueStore backed by Redis, for sharing state across replicas."""

    def __init__(self, redis_url: str) -> None:
        """Initializes the store.

        Args:
            redis_url: Connection URL, e.g. 'redis://host:6379/0'.
        """
        self._client: redis.Redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        """Returns the value for key, or None if not present.

        Args:
            key: The key to look up.

        Returns:
            The stored value, or None.
        """
        value = await self._client.get(key)
        return str(value) if value is not None else None

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """Stores value under key, optionally expiring after ttl_seconds.

        Args:
            key: The key to store under.
            value: The value to store.
            ttl_seconds: Expiry, in seconds. None means no expiry.
        """
        await self._client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        """Removes key, if present.

        Args:
            key: The key to remove.
        """
        await self._client.delete(key)

    def lock(
        self, key: str, timeout_seconds: float = 30
    ) -> AbstractAsyncContextManager[object]:
        """Returns a real distributed lock for key, shared across replicas.

        Args:
            key: The key to lock.
            timeout_seconds: Auto-expires the lock after this long, so a
                replica that crashes mid-refresh can't hold it forever.
        """
        return self._client.lock(key, timeout=timeout_seconds)

    async def aclose(self) -> None:
        """Closes the underlying Redis connection pool."""
        await self._client.aclose()
