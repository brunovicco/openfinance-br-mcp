"""Unit tests for NubankAdapter.list_transactions and the
list_transactions tool function's categorization logic.

Uses respx to intercept HTTP calls without real network access,
keeping tests fast and deterministic. Protocol-level dispatch (schema
validation, structuredContent, error translation) is covered by
tests/integration/test_tool_dispatch.py instead of here.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from openfinance_br_mcp.adapters.nubank import _NUBANK_BASE, NubankAdapter
from openfinance_br_mcp.auth.token import TokenResponse, TokenStore
from openfinance_br_mcp.context import AppContext
from openfinance_br_mcp.schemas.transaction import (
    CreditDebitType,
    PaymentType,
    Transaction,
    TransactionFilters,
    TransactionList,
    TransactionType,
)
from openfinance_br_mcp.tools.categorizer import TransactionCategorizer
from openfinance_br_mcp.tools.transactions import list_transactions

SUBJECT_ID = "12345678900"
ACCOUNT_ID = "acc_test_001"


@pytest.fixture
def fresh_token() -> TokenResponse:
    """Valid token for use in the tests."""
    return TokenResponse(
        {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh",
            "expires_in": 3600,
            "_obtained_at": datetime.now(UTC),
        }
    )


@pytest.fixture
async def token_store(fresh_token: TokenResponse) -> TokenStore:
    """TokenStore preloaded with a token."""
    store = TokenStore()
    await store.save("nubank", SUBJECT_ID, fresh_token)
    return store


def _fake_ctx(app_context: AppContext) -> SimpleNamespace:
    """Minimal stand-in for an MCP ``Context``, exposing only the
    ``request_context.lifespan_context`` attribute chain tool functions
    actually read."""
    return SimpleNamespace(
        request_context=SimpleNamespace(lifespan_context=app_context)
    )


def _sample_transaction() -> Transaction:
    return Transaction(
        transaction_id="tx_001",
        completed_authorised_payment_type=PaymentType.DEBITO,
        credit_debit_type=CreditDebitType.DEBITO,
        transaction_name="COMPRA IFOOD",
        type=TransactionType.PIX,
        amount=Decimal("45.90"),
        transaction_date=date(2024, 3, 15),
    )


class TestNubankAdapterTransactions:
    """Tests for NubankAdapter's list_transactions method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_transactions_returns_parsed_list(
        self, token_store: TokenStore, sample_transaction_response: dict
    ) -> None:
        """list_transactions should return a TransactionList with parsed data."""
        url = f"{_NUBANK_BASE}/accounts/v2/accounts/{ACCOUNT_ID}/transactions"
        respx.get(url).mock(
            return_value=httpx.Response(200, json=sample_transaction_response)
        )

        async with httpx.AsyncClient() as client:
            adapter = NubankAdapter(token_store, client)
            filters = TransactionFilters(account_id=ACCOUNT_ID)
            result = await adapter.list_transactions(SUBJECT_ID, filters)

        assert result.total_records == 2
        assert len(result.data) == 2
        assert result.data[0].transaction_id == "tx_001"
        assert result.data[0].credit_debit_type == CreditDebitType.DEBITO
        assert result.data[0].amount == Decimal("45.90")

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_transactions_http_error_raises(
        self, token_store: TokenStore
    ) -> None:
        """An HTTP 500 should raise BankAdapterError."""
        from openfinance_br_mcp.exceptions import BankAdapterError

        url = f"{_NUBANK_BASE}/accounts/v2/accounts/{ACCOUNT_ID}/transactions"
        respx.get(url).mock(return_value=httpx.Response(500))

        async with httpx.AsyncClient() as client:
            adapter = NubankAdapter(token_store, client)
            filters = TransactionFilters(account_id=ACCOUNT_ID)

            with pytest.raises(BankAdapterError) as exc_info:
                await adapter.list_transactions(SUBJECT_ID, filters)

        assert exc_info.value.bank_id == "nubank"
        assert exc_info.value.status_code == 500


class TestListTransactionsCategorization:
    """Tests for the list_transactions tool function's categorization logic."""

    @pytest.mark.asyncio
    async def test_categorize_false_leaves_category_unset(self) -> None:
        """Without categorize=True, transactions keep category=None."""
        mock_adapter = AsyncMock()
        mock_adapter.list_transactions.return_value = TransactionList(
            data=[_sample_transaction()], total_records=1, total_pages=1
        )
        mock_categorizer = AsyncMock(spec=TransactionCategorizer)
        app = AppContext(
            http_client=AsyncMock(),
            token_store=AsyncMock(),
            adapters={"nubank": mock_adapter},
            categorizer=mock_categorizer,
            consent_manager=AsyncMock(),
            authorization_sessions=AsyncMock(),
            principal_bindings=AsyncMock(),
            payment_consent_manager=AsyncMock(),
            idempotency_store=AsyncMock(),
            directory=None,
        )

        result = await list_transactions(
            subject_id=SUBJECT_ID,
            bank="nubank",
            account_id=ACCOUNT_ID,
            ctx=_fake_ctx(app),
        )

        assert result.categorized is False
        assert result.transactions[0].category is None
        mock_categorizer.categorize_batch.assert_not_called()

    @pytest.mark.asyncio
    async def test_categorize_true_enriches_transactions(self) -> None:
        """With categorize=True, each transaction gets a category from
        the categorizer."""
        mock_adapter = AsyncMock()
        mock_adapter.list_transactions.return_value = TransactionList(
            data=[_sample_transaction()], total_records=1, total_pages=1
        )
        mock_categorizer = AsyncMock(spec=TransactionCategorizer)
        mock_categorizer.categorize_batch.return_value = [("food", 0.95)]
        app = AppContext(
            http_client=AsyncMock(),
            token_store=AsyncMock(),
            adapters={"nubank": mock_adapter},
            categorizer=mock_categorizer,
            consent_manager=AsyncMock(),
            authorization_sessions=AsyncMock(),
            principal_bindings=AsyncMock(),
            payment_consent_manager=AsyncMock(),
            idempotency_store=AsyncMock(),
            directory=None,
        )

        result = await list_transactions(
            subject_id=SUBJECT_ID,
            bank="nubank",
            account_id=ACCOUNT_ID,
            ctx=_fake_ctx(app),
            categorize=True,
        )

        assert result.categorized is True
        assert result.transactions[0].category == "food"
        mock_categorizer.categorize_batch.assert_called_once()
