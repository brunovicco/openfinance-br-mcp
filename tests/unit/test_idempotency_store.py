"""Unit tests for auth/idempotency_store.py."""

import pytest

from openfinance_br_mcp.auth.idempotency_store import (
    IdempotencyConflictError,
    IdempotencyStore,
)

BANK_ID = "nubank"
SUBJECT_ID = "12345678900"
IDEMPOTENCY_KEY = "idem-key-1"
PAYLOAD = {"amount": "150.00", "creditor_key": "someone@example.com"}


class TestGetOrCompute:
    """Tests for IdempotencyStore.get_or_compute()."""

    @pytest.mark.asyncio
    async def test_first_call_invokes_compute_and_stores_result(self) -> None:
        store = IdempotencyStore()
        calls = 0

        async def _compute() -> str:
            nonlocal calls
            calls += 1
            return '{"payment_id": "abc"}'

        result = await store.get_or_compute(
            bank_id=BANK_ID,
            subject_id=SUBJECT_ID,
            idempotency_key=IDEMPOTENCY_KEY,
            payload=PAYLOAD,
            compute=_compute,
        )

        assert result == '{"payment_id": "abc"}'
        assert calls == 1

    @pytest.mark.asyncio
    async def test_identical_replay_returns_cached_result_without_recompute(
        self,
    ) -> None:
        store = IdempotencyStore()
        calls = 0

        async def _compute() -> str:
            nonlocal calls
            calls += 1
            return f'{{"payment_id": "call-{calls}"}}'

        first = await store.get_or_compute(
            bank_id=BANK_ID,
            subject_id=SUBJECT_ID,
            idempotency_key=IDEMPOTENCY_KEY,
            payload=PAYLOAD,
            compute=_compute,
        )
        second = await store.get_or_compute(
            bank_id=BANK_ID,
            subject_id=SUBJECT_ID,
            idempotency_key=IDEMPOTENCY_KEY,
            payload=PAYLOAD,
            compute=_compute,
        )

        assert first == second == '{"payment_id": "call-1"}'
        assert calls == 1

    @pytest.mark.asyncio
    async def test_same_key_with_different_payload_raises_conflict(self) -> None:
        store = IdempotencyStore()

        async def _compute() -> str:
            return '{"payment_id": "abc"}'

        await store.get_or_compute(
            bank_id=BANK_ID,
            subject_id=SUBJECT_ID,
            idempotency_key=IDEMPOTENCY_KEY,
            payload=PAYLOAD,
            compute=_compute,
        )

        with pytest.raises(IdempotencyConflictError, match="already used"):
            await store.get_or_compute(
                bank_id=BANK_ID,
                subject_id=SUBJECT_ID,
                idempotency_key=IDEMPOTENCY_KEY,
                payload={**PAYLOAD, "amount": "999.00"},
                compute=_compute,
            )

    @pytest.mark.asyncio
    async def test_same_key_different_bank_does_not_collide(self) -> None:
        """Same subject + same idempotency_key at two different banks
        must not share a cache entry - mirrors TokenStore/ConsentManager's
        composite-key rationale (a single key colliding across banks would
        silently misattribute one bank's payment record to another)."""
        store = IdempotencyStore()

        async def _compute_a() -> str:
            return '{"payment_id": "bank-a"}'

        async def _compute_b() -> str:
            return '{"payment_id": "bank-b"}'

        result_a = await store.get_or_compute(
            bank_id="nubank",
            subject_id=SUBJECT_ID,
            idempotency_key=IDEMPOTENCY_KEY,
            payload=PAYLOAD,
            compute=_compute_a,
        )
        result_b = await store.get_or_compute(
            bank_id="sicoob",
            subject_id=SUBJECT_ID,
            idempotency_key=IDEMPOTENCY_KEY,
            payload=PAYLOAD,
            compute=_compute_b,
        )

        assert result_a == '{"payment_id": "bank-a"}'
        assert result_b == '{"payment_id": "bank-b"}'
