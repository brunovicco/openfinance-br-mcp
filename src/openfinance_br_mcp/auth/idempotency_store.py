"""Persistent, cross-replica idempotency store for PIX payment initiation.

Replaces the in-process ``dict`` previously used
(``AppContext.pix_idempotency_cache``), which never survived a process
restart and wasn't shared across Kubernetes replicas - two requests
carrying the same ``idempotency_key`` landing on different replicas
could both reach the bank. Backed by the same pluggable
``KeyValueStore`` as ``TokenStore``/``ConsentManager`` (Redis in
production, see auth/redis_backend.py).

The Open Finance Brasil idempotency contract is stricter than "same
key returns the same result": a replay with an *identical* payload
under a previously-used key returns the cached response, but a replay
with a *different* payload under the same key must be rejected - it
almost certainly signals a client bug (reusing a UUID) rather than a
legitimate retry. This module enforces that distinction by hashing the
request payload alongside the key.

Example:
    >>> store = IdempotencyStore()
    >>> async def _do_payment() -> str:
    ...     return '{"payment_id": "abc"}'
    >>> result = await store.get_or_compute(
    ...     bank_id="nubank", subject_id="123", idempotency_key="k1",
    ...     payload={"amount": "10.00"}, compute=_do_payment,
    ... )
"""

import hashlib
import json
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore
from openfinance_br_mcp.exceptions import ValidationError

log = structlog.get_logger(__name__)

_KEY_PREFIX = "openfinance:pix_idempotency:"

# Kept well above any plausible payment-consent lifetime the Payments
# API grants, so a legitimate late retry never falls outside the
# idempotency window; must not be indefinite, since these records
# would otherwise accumulate forever in the shared store.
_DEFAULT_TTL_SECONDS = 7 * 24 * 60 * 60


class IdempotencyConflictError(ValidationError):
    """The same idempotency_key was reused with a different payload.

    Distinct from a legitimate replay (identical key + identical
    payload, which returns the cached response) - this signals the
    caller reused a key across two different payment requests, which
    the Open Finance Brasil idempotency contract requires rejecting
    outright rather than silently executing (or silently returning the
    unrelated cached result for) the new one.
    """


def _composite_key(bank_id: str, subject_id: str, idempotency_key: str) -> str:
    """Builds the store key for one idempotency record.

    Args:
        bank_id: Identifier of the bank the payment was initiated at.
        subject_id: Identifier of the paying user.
        idempotency_key: Client-supplied idempotency key.

    Returns:
        The composite key.
    """
    return f"{_KEY_PREFIX}{bank_id}:{subject_id}:{idempotency_key}"


def _payload_hash(payload: dict[str, Any]) -> str:
    """Computes a deterministic hash of a payment payload.

    Uses a canonical (sorted-keys, no whitespace) JSON encoding so two
    semantically identical payloads hash identically regardless of key
    insertion order.

    Args:
        payload: The payment request payload (pre-signing, plain dict).

    Returns:
        Hex-encoded SHA-256 digest of the canonical payload.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


class IdempotencyStore:
    """Persists PIX idempotency records, safe across replicas and restarts.

    Attributes:
        _store: Underlying key-value store, also the source of the
            per-key lock used to make check-then-compute-then-save
            atomic (mirrors TokenStore's refresh-idempotency pattern in
            auth/token.py).
        _ttl_seconds: How long an idempotency record is retained.
    """

    def __init__(
        self,
        store: KeyValueStore | None = None,
        ttl_seconds: int = _DEFAULT_TTL_SECONDS,
    ) -> None:
        """Initializes the store.

        Args:
            store: Backing KeyValueStore. Defaults to a new
                InMemoryStore (fine for mock mode/local dev; pass a
                RedisStore in production - see context.py).
            ttl_seconds: How long to retain each idempotency record.
        """
        self._store: KeyValueStore = store if store is not None else InMemoryStore()
        self._ttl_seconds = ttl_seconds

    async def get_or_compute(
        self,
        *,
        bank_id: str,
        subject_id: str,
        idempotency_key: str,
        payload: dict[str, Any],
        compute: Callable[[], Awaitable[str]],
    ) -> str:
        """Returns a cached response for an identical replay, else computes one.

        The entire check-compute-store sequence runs under a per-key
        lock, so two concurrent requests carrying the same
        idempotency_key can't both slip past the cache check and both
        reach the bank.

        Args:
            bank_id: Identifier of the bank the payment is initiated at.
            subject_id: Identifier of the paying user.
            idempotency_key: Client-supplied idempotency key.
            payload: The payment request payload, used to detect key
                reuse across different payments.
            compute: Async callable that performs the actual payment
                and returns its serialized (JSON string) result. Only
                invoked when no prior record exists for this key.

        Returns:
            The serialized payment result - either freshly computed or
            replayed from a prior identical request.

        Raises:
            IdempotencyConflictError: If idempotency_key was already
                used by this subject/bank with a different payload.
        """
        key = _composite_key(bank_id, subject_id, idempotency_key)
        new_hash = _payload_hash(payload)

        async with self._store.lock(key):
            raw = await self._store.get(key)
            if raw is not None:
                record = json.loads(raw)
                if record["payload_hash"] != new_hash:
                    log.warning(
                        "idempotency_key_conflict",
                        bank_id=bank_id,
                        subject_id=subject_id,
                    )
                    raise IdempotencyConflictError(
                        f"idempotency_key '{idempotency_key}' was already used "
                        "with a different payment payload - generate a new "
                        "idempotency_key for a different payment.",
                        code="IDEMPOTENCY_KEY_CONFLICT",
                    )
                log.info("idempotency_replay", bank_id=bank_id, subject_id=subject_id)
                return str(record["response"])

            response = await compute()
            record = {"payload_hash": new_hash, "response": response}
            await self._store.set(
                key, json.dumps(record), ttl_seconds=self._ttl_seconds
            )
            log.info("idempotency_recorded", bank_id=bank_id, subject_id=subject_id)
            return response
