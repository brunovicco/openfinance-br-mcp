"""Pluggable key-value store for TokenStore/ConsentManager.

``TokenStore`` (auth/token.py) and ``ConsentManager`` (auth/consent.py)
need a shared backend for a Kubernetes Deployment running multiple
replicas behind one Service: a consent completed on one replica (e.g.
``complete_consent`` hitting pod A) must be visible to another (a
later ``check_consent_status``/``list_accounts`` call landing on pod
B). ``KeyValueStore`` is the minimal interface both need.

``InMemoryStore`` below is the default, correct for a
single-process/mock-mode deployment. See auth/redis_backend.py for the
shared, multi-replica-safe implementation.

Values are always strings (JSON-encoded by the caller) - this
interface deliberately doesn't know about TokenResponse or consent
payload shapes, so it can be backed by anything that stores strings.

``lock()`` provides mutual exclusion per key. ``InMemoryStore``'s is an
in-process ``asyncio.Lock``. ``RedisStore``'s is a real distributed
lock backed by Redis (SET NX + TTL under the hood), so refresh
idempotency holds across replicas, not just within one process.

Example:
    >>> store: KeyValueStore = InMemoryStore()
    >>> await store.set("token:user123", '{"access_token": "..."}')
    >>> raw = await store.get("token:user123")
    >>> async with store.lock("token:user123"):
    ...     ...  # mutually exclusive per key
"""

import asyncio
from contextlib import AbstractAsyncContextManager
from typing import Protocol


class KeyValueStore(Protocol):
    """Minimal async string key-value store."""

    async def get(self, key: str) -> str | None:
        """Returns the value for key, or None if not present."""
        ...

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """Stores value under key, optionally expiring after ttl_seconds."""
        ...

    async def delete(self, key: str) -> None:
        """Removes key. A no-op if key doesn't exist."""
        ...

    def lock(
        self, key: str, timeout_seconds: float = 30
    ) -> AbstractAsyncContextManager[object]:
        """Returns an async context manager providing mutual exclusion for key.

        Args:
            key: The key to lock.
            timeout_seconds: Auto-expires the lock after this long, so a
                crashed holder can't deadlock other callers forever.
        """
        ...


class InMemoryStore:
    """Default, single-process, non-shared store - today's behavior.

    TTL is intentionally not enforced here: this store never survives
    a process restart anyway, and TokenResponse.is_expired() already
    determines expiry from the value's own embedded timestamp, not
    from the store.
    """

    def __init__(self) -> None:
        """Initializes an empty store."""
        self._data: dict[str, str] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get(self, key: str) -> str | None:
        """Returns the value for key, or None if not present.

        Args:
            key: The key to look up.

        Returns:
            The stored value, or None.
        """
        return self._data.get(key)

    def lock(
        self, key: str, timeout_seconds: float = 30
    ) -> AbstractAsyncContextManager[object]:
        """Returns (creating if needed) an in-process lock for key.

        Args:
            key: The key to lock.
            timeout_seconds: Unused - an in-process asyncio.Lock can't
                deadlock across process crashes the way a distributed
                lock can, so there's nothing to auto-expire here.
        """
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """Stores value under key. ttl_seconds is ignored (see class docstring).

        Args:
            key: The key to store under.
            value: The value to store.
            ttl_seconds: Ignored by this backend.
        """
        self._data[key] = value

    async def delete(self, key: str) -> None:
        """Removes key, if present.

        Args:
            key: The key to remove.
        """
        self._data.pop(key, None)
