"""Unit tests for tools/accounts.py.

Uses MockOpenFinanceAdapter (already covered by test_mock_adapter.py)
to exercise the tool wrapper logic in isolation, without needing
respx/real HTTP mocking. Protocol-level dispatch is covered by
tests/integration/test_tool_dispatch.py instead of here.
"""

import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from openfinance_br_mcp.adapters.mock_adapter import MockOpenFinanceAdapter
from openfinance_br_mcp.context import AppContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.tools.accounts import get_balance, list_accounts

SUBJECT_ID = "12345678900"


def _app(adapter: MockOpenFinanceAdapter | None) -> AppContext:
    return AppContext(
        http_client=httpx.AsyncClient(),
        token_store=AsyncMock(),
        adapters={"nubank": adapter} if adapter else {},
        categorizer=AsyncMock(),
        consent_manager=AsyncMock(),
        authorization_sessions=AsyncMock(),
        principal_bindings=AsyncMock(),
        payment_consent_manager=AsyncMock(),
        idempotency_store=AsyncMock(),
        directory=None,
    )


def _fake_ctx(app_context: AppContext) -> SimpleNamespace:
    return SimpleNamespace(
        request_context=SimpleNamespace(lifespan_context=app_context)
    )


class TestListAccounts:
    """Tests for list_accounts()."""

    @pytest.mark.asyncio
    async def test_returns_accounts_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(list_accounts)(
            SUBJECT_ID, "nubank", _fake_ctx(app)
        )

        assert result.bank == "nubank"
        assert result.total_records == 1
        assert result.accounts[0].account_id == "mock-acc-001"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(list_accounts)(SUBJECT_ID, "nubank", _fake_ctx(app))


class TestGetBalance:
    """Tests for get_balance()."""

    @pytest.mark.asyncio
    async def test_returns_balance_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(get_balance)(
            SUBJECT_ID, "nubank", "acc-1", _fake_ctx(app)
        )

        assert result.bank == "nubank"
        assert result.balance.account_id == "acc-1"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(get_balance)(
                SUBJECT_ID, "nubank", "acc-1", _fake_ctx(app)
            )
