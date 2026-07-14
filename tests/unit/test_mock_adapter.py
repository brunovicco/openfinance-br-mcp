"""Unit tests for MockOpenFinanceAdapter.

These exercise the mock adapter directly (not through the MCP
protocol layer - see tests/integration/test_tool_dispatch.py for
that), confirming every BankAdapter method returns well-formed,
schema-valid canned data without any network access.
"""

import pytest

from openfinance_br_mcp.adapters.mock_adapter import MockOpenFinanceAdapter
from openfinance_br_mcp.schemas.pix import PixKeyType, PixPaymentRequest

SUBJECT_ID = "12345678900"


@pytest.fixture
def adapter() -> MockOpenFinanceAdapter:
    return MockOpenFinanceAdapter("nubank")


class TestMockOpenFinanceAdapter:
    """Tests for MockOpenFinanceAdapter's canned responses."""

    def test_bank_id_reflects_constructor_argument(self) -> None:
        """Each instance impersonates the bank it was constructed for."""
        assert MockOpenFinanceAdapter("caixa").bank_id == "caixa"

    @pytest.mark.asyncio
    async def test_get_accounts_returns_one_account(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        result = await adapter.get_accounts(SUBJECT_ID)
        assert result.total_records == 1
        assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_get_balance_returns_fixed_balance(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        balance = await adapter.get_balance(SUBJECT_ID, "any-account-id")
        assert balance.account_id == "any-account-id"
        assert balance.available_amount > 0

    @pytest.mark.asyncio
    async def test_list_transactions_returns_two_transactions(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        from openfinance_br_mcp.schemas.transaction import TransactionFilters

        result = await adapter.list_transactions(
            SUBJECT_ID, TransactionFilters(account_id="any-account-id")
        )
        assert result.total_records == 2
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_get_credit_card_accounts_returns_one_card(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        cards = await adapter.get_credit_card_accounts(SUBJECT_ID)
        assert len(cards) == 1

    @pytest.mark.asyncio
    async def test_get_credit_card_bills_returns_one_bill(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        bills = await adapter.get_credit_card_bills(SUBJECT_ID, "any-card-id")
        assert len(bills) == 1

    @pytest.mark.asyncio
    async def test_list_pix_keys_returns_one_key(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        keys = await adapter.list_pix_keys(SUBJECT_ID, "any-account-id")
        assert len(keys) == 1
        assert keys[0].account_id == "any-account-id"

    @pytest.mark.asyncio
    async def test_initiate_pix_echoes_amount_and_idempotency_key(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        request = PixPaymentRequest(
            amount="150.00",  # type: ignore[arg-type]
            creditor_key="someone@example.com",
            creditor_key_type=PixKeyType.EMAIL,
            debtor_account_id="any-account-id",
            idempotency_key="11111111-1111-1111-1111-111111111111",
        )
        payment = await adapter.initiate_pix(SUBJECT_ID, request)
        assert payment.amount == request.amount
        assert "11111111" in payment.payment_id

    @pytest.mark.asyncio
    async def test_list_investments_returns_one_investment(
        self, adapter: MockOpenFinanceAdapter
    ) -> None:
        result = await adapter.list_investments(SUBJECT_ID)
        assert result.total_records == 1
        assert len(result.data) == 1
