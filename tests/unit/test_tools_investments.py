"""Unit tests for tools/investments.py.

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
from openfinance_br_mcp.tools.investments import list_investments

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
        directory=None,
    )


def _fake_ctx(app_context: AppContext) -> SimpleNamespace:
    return SimpleNamespace(
        request_context=SimpleNamespace(lifespan_context=app_context)
    )


class TestListInvestments:
    """Tests for list_investments()."""

    @pytest.mark.asyncio
    async def test_returns_investments_and_summary_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(list_investments)(
            SUBJECT_ID, "nubank", _fake_ctx(app)
        )

        assert result.bank == "nubank"
        assert result.total_records == 1
        assert result.investments[0].investment_id == "mock-inv-001"
        assert result.summary.total_gross_amount == 10500.00
        assert result.summary.total_net_amount == 9800.00

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(list_investments)(SUBJECT_ID, "nubank", _fake_ctx(app))
