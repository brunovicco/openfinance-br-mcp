"""Unit tests for tools/credit_cards.py.

See test_tools_accounts.py's module docstring for the testing approach.
"""

import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from openfinance_br_mcp.adapters.mock_adapter import MockOpenFinanceAdapter
from openfinance_br_mcp.context import AppContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.tools.credit_cards import (
    get_credit_card_bills,
    list_credit_cards,
)

SUBJECT_ID = "12345678900"


def _app(adapter: MockOpenFinanceAdapter | None) -> AppContext:
    return AppContext(
        http_client=httpx.AsyncClient(),
        token_store=AsyncMock(),
        adapters={"nubank": adapter} if adapter else {},
        categorizer=AsyncMock(),
        consent_manager=AsyncMock(),
        authorization_sessions=AsyncMock(),
        directory=None,
    )


def _fake_ctx(app_context: AppContext) -> SimpleNamespace:
    return SimpleNamespace(
        request_context=SimpleNamespace(lifespan_context=app_context)
    )


class TestListCreditCards:
    """Tests for list_credit_cards()."""

    @pytest.mark.asyncio
    async def test_returns_cards_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(list_credit_cards)(
            SUBJECT_ID, "nubank", _fake_ctx(app)
        )

        assert result.bank == "nubank"
        assert result.credit_cards[0].credit_card_account_id == "mock-cc-001"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(list_credit_cards)(
                SUBJECT_ID, "nubank", _fake_ctx(app)
            )


class TestGetCreditCardBills:
    """Tests for get_credit_card_bills()."""

    @pytest.mark.asyncio
    async def test_returns_bills_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(get_credit_card_bills)(
            SUBJECT_ID, "nubank", "mock-cc-001", _fake_ctx(app)
        )

        assert result.bank == "nubank"
        assert result.credit_card_account_id == "mock-cc-001"
        assert result.bills[0].bill_id == "mock-bill-001"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(get_credit_card_bills)(
                SUBJECT_ID, "nubank", "mock-cc-001", _fake_ctx(app)
            )
