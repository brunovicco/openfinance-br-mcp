"""Unit tests for tools/categorizer.py.

Uses DSPy's own DummyLM test double (dspy.utils.dummies.DummyLM)
instead of mocking dspy.Predict directly - it exercises the real
DSPy prediction/parsing pipeline, just swapping out the network call
to a real LLM, so a genuinely malformed LM response still surfaces
DSPy's real parsing errors (see test_raises_categorization_error_on_malformed_response).

Each test wraps its categorize()/categorize_batch() call in
dspy.context(lm=...) rather than the global dspy.configure(): DSPy
ties dspy.configure() to whichever async task first calls it (a real
behavior discovered running these tests, not assumed - it raises
RuntimeError from any other task, and pytest-asyncio runs each test
in its own task), while dspy.context() is explicitly the
task-scoped, test-safe alternative.
"""

import dspy
import pytest
from dspy.utils.dummies import DummyLM
from pydantic import SecretStr

from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import CategorizationError
from openfinance_br_mcp.tools.categorizer import (
    TransactionCategorizer,
    TransactionSignature,
    get_categorizer,
)


@pytest.fixture(autouse=True)
def _reset_get_categorizer_cache() -> None:
    """get_categorizer() is lru_cache'd process-wide - clear it so tests
    don't leak a TransactionCategorizer instance across test runs."""
    get_categorizer.cache_clear()
    yield
    get_categorizer.cache_clear()


def _initialized_categorizer() -> TransactionCategorizer:
    """Builds a categorizer with a real dspy.Predict, bypassing the real
    dspy.LM/Anthropic API construction in _ensure_initialized(). The
    caller is responsible for wrapping calls in dspy.context(lm=...)."""
    categorizer = TransactionCategorizer()
    categorizer._initialized = True
    categorizer._predictor = dspy.Predict(TransactionSignature)
    return categorizer


class TestEnsureInitialized:
    """Tests for TransactionCategorizer._ensure_initialized()."""

    def test_raises_without_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "anthropic_api_key", None)
        categorizer = TransactionCategorizer()

        with pytest.raises(CategorizationError, match="ANTHROPIC_API_KEY"):
            categorizer._ensure_initialized()

    def test_only_constructs_the_lm_once(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "anthropic_api_key", SecretStr("fake-key"))
        construct_count = 0

        class _FakeLM:
            def __init__(self, **kwargs) -> None:
                nonlocal construct_count
                construct_count += 1

        monkeypatch.setattr("openfinance_br_mcp.tools.categorizer.dspy.LM", _FakeLM)
        categorizer = TransactionCategorizer()

        categorizer._ensure_initialized()
        categorizer._ensure_initialized()

        assert construct_count == 1
        assert categorizer._initialized is True


class TestCategorize:
    """Tests for TransactionCategorizer.categorize()."""

    @pytest.mark.asyncio
    async def test_returns_category_and_confidence(self) -> None:
        categorizer = _initialized_categorizer()

        with dspy.context(lm=DummyLM([{"category": "food", "confidence": 0.9}])):
            category, confidence = await categorizer.categorize(
                "COMPRA IFOOD*REFEICAO", -45.90
            )

        assert category == "food"
        assert confidence == 0.9

    @pytest.mark.asyncio
    async def test_unknown_category_falls_back_to_other(self) -> None:
        categorizer = _initialized_categorizer()

        with dspy.context(
            lm=DummyLM([{"category": "not_a_real_category", "confidence": 0.9}])
        ):
            category, confidence = await categorizer.categorize("X", 1.0)

        assert category == "other"
        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_confidence_is_clamped_to_valid_range(self) -> None:
        categorizer = _initialized_categorizer()

        with dspy.context(lm=DummyLM([{"category": "food", "confidence": 5.0}])):
            _, confidence = await categorizer.categorize("X", 1.0)

        assert confidence == 1.0

    @pytest.mark.asyncio
    async def test_negative_confidence_is_clamped_to_zero(self) -> None:
        categorizer = _initialized_categorizer()

        with dspy.context(lm=DummyLM([{"category": "food", "confidence": -1.0}])):
            _, confidence = await categorizer.categorize("X", 1.0)

        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_raises_categorization_error_on_malformed_response(self) -> None:
        """A response DSPy can't parse into the expected output fields
        must surface as CategorizationError, not a raw DSPy exception."""
        categorizer = _initialized_categorizer()

        with (
            dspy.context(lm=DummyLM([{"category": "food"}])),  # missing confidence
            pytest.raises(CategorizationError, match="Categorization failed"),
        ):
            await categorizer.categorize("X", 1.0)


class TestCategorizeBatch:
    """Tests for TransactionCategorizer.categorize_batch()."""

    @pytest.mark.asyncio
    async def test_categorizes_each_transaction_in_order(self) -> None:
        categorizer = _initialized_categorizer()

        with dspy.context(
            lm=DummyLM(
                [
                    {"category": "food", "confidence": 0.9},
                    {"category": "transport", "confidence": 0.8},
                ]
            )
        ):
            results = await categorizer.categorize_batch(
                [("IFOOD", -45.90), ("UBER", -20.00)]
            )

        assert results == [("food", 0.9), ("transport", 0.8)]

    @pytest.mark.asyncio
    async def test_failing_transaction_falls_back_without_stopping_the_batch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """categorize_batch()'s per-item try/except is pure control flow,
        not a DSPy parsing concern (already covered by TestCategorize) -
        mocking categorize() directly isolates that logic cleanly."""
        categorizer = _initialized_categorizer()
        calls = iter(
            [
                CategorizationError("boom", code="DSPY_PREDICT_ERROR"),
                ("transport", 0.8),
            ]
        )

        async def fake_categorize(description: str, amount: float):
            outcome = next(calls)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        monkeypatch.setattr(categorizer, "categorize", fake_categorize)

        results = await categorizer.categorize_batch([("BAD", -1.0), ("UBER", -20.00)])

        assert results == [("other", 0.0), ("transport", 0.8)]


def test_get_categorizer_returns_a_singleton() -> None:
    first = get_categorizer()
    second = get_categorizer()

    assert first is second
