"""Intelligent transaction categorization module via DSPy.

Uses DSPy with a Claude model to classify financial transactions
into predefined categories. DSPy is appropriate here because
categorization is an LLM classification/routing problem: there are
no deterministic rules that reliably cover every transaction
description across different Brazilian banks.

The module uses ``dspy.Predict`` with caching enabled to avoid
redundant API calls for identical transactions.

Example:
    >>> categorizer = TransactionCategorizer()
    >>> category = await categorizer.categorize("COMPRA IFOOD*REFEICAO", 45.90)
    >>> print(category)
    'food'
"""

from functools import lru_cache

import dspy
import structlog

from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import CategorizationError

log = structlog.get_logger(__name__)

VALID_CATEGORIES = frozenset(
    {
        "food",
        "transport",
        "utilities",
        "health",
        "entertainment",
        "shopping",
        "education",
        "travel",
        "income",
        "transfer",
        "investment",
        "taxes",
        "other",
    }
)


class TransactionSignature(dspy.Signature):  # type: ignore[misc]
    """Classifies a Brazilian bank transaction into a category.

    Analyzes the description and amount to infer the most likely
    category. Always returns one of the valid categories in the enum.
    """

    transaction_description: str = dspy.InputField(
        desc="Transaction description as it appears on a Brazilian bank statement"
    )
    amount: float = dspy.InputField(
        desc="Amount in BRL (positive=credit, negative=debit)"
    )
    category: str = dspy.OutputField(
        desc=(
            "One of the categories: food, transport, utilities, health, entertainment, "
            "shopping, education, travel, income, transfer, investment, taxes, other"
        )
    )
    confidence: float = dspy.OutputField(desc="Confidence score between 0.0 and 1.0")


class TransactionCategorizer:
    """Categorizes financial transactions using DSPy + Claude.

    Lazily initializes the DSPy predictor on first call to avoid
    unnecessary initialization when the module is never used.

    Attributes:
        _predictor: DSPy predictor instance, initialized on demand.
        _initialized: Lazy-initialization flag.
    """

    def __init__(self) -> None:
        """Initializes the categorizer without activating the LLM yet."""
        self._predictor: dspy.Predict | None = None
        self._initialized: bool = False

    def _ensure_initialized(self) -> None:
        """Ensures DSPy is configured before use.

        Configures the LM with credentials from Settings and enables
        caching.

        Raises:
            CategorizationError: If the API key is not configured.
        """
        if self._initialized:
            return

        if not settings.anthropic_api_key:
            raise CategorizationError(
                "ANTHROPIC_API_KEY is not configured - DSPy categorization is disabled",
                code="DSPY_NO_API_KEY",
            )

        lm = dspy.LM(
            model=settings.dspy_model,
            api_key=settings.anthropic_api_key.get_secret_value(),
            cache=settings.dspy_cache_enabled,
        )
        dspy.configure(lm=lm)
        self._predictor = dspy.Predict(TransactionSignature)
        self._initialized = True
        log.info("dspy_initialized", model=settings.dspy_model)

    async def categorize(
        self,
        description: str,
        amount: float,
    ) -> tuple[str, float]:
        """Categorizes a single transaction.

        Args:
            description: Transaction description on the statement.
            amount: Amount in BRL (debit as negative).

        Returns:
            Tuple (category, confidence) where category is one of the
            VALID_CATEGORIES strings and confidence is a float 0.0-1.0.

        Raises:
            CategorizationError: If the LLM call fails.
        """
        self._ensure_initialized()
        assert self._predictor is not None

        try:
            result = self._predictor(
                transaction_description=description,
                amount=float(amount),
            )
            category = result.category.lower().strip()
            confidence = float(result.confidence)
        except Exception as exc:
            log.warning(
                "categorization_failed", description=description, error=str(exc)
            )
            raise CategorizationError(
                f"Categorization failed: {exc}",
                code="DSPY_PREDICT_ERROR",
            ) from exc

        if category not in VALID_CATEGORIES:
            log.warning(
                "invalid_category_returned",
                category=category,
                description=description,
            )
            category = "other"
            confidence = 0.0

        return category, min(max(confidence, 0.0), 1.0)

    async def categorize_batch(
        self,
        transactions: list[tuple[str, float]],
    ) -> list[tuple[str, float]]:
        """Categorizes a batch of transactions with graceful fallback.

        Transactions that fail individually get ('other', 0.0) without
        interrupting the rest of the batch.

        Args:
            transactions: List of (description, amount).

        Returns:
            List of (category, confidence) in the same order.
        """
        results: list[tuple[str, float]] = []
        for description, amount in transactions:
            try:
                cat, conf = await self.categorize(description, amount)
            except CategorizationError:
                cat, conf = "other", 0.0
            results.append((cat, conf))
        return results


@lru_cache(maxsize=1)
def get_categorizer() -> TransactionCategorizer:
    """Returns the singleton instance of the categorizer.

    The ``lru_cache`` guarantees that only one DSPy instance is
    created per process, reusing DSPy's internal cache.

    Returns:
        Shared TransactionCategorizer instance.
    """
    return TransactionCategorizer()
