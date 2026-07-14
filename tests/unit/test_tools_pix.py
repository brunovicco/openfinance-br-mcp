"""Unit tests for tools/pix.py.

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
from openfinance_br_mcp.schemas.pix import PixKeyType
from openfinance_br_mcp.tools.pix import initiate_pix, list_pix_keys

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


class TestListPixKeys:
    """Tests for list_pix_keys()."""

    @pytest.mark.asyncio
    async def test_returns_keys_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(list_pix_keys)(
            SUBJECT_ID, "nubank", "acc-1", _fake_ctx(app)
        )

        assert result.bank == "nubank"
        assert result.account_id == "acc-1"
        assert result.pix_keys[0].key == "mock-user@nubank.example"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(list_pix_keys)(
                SUBJECT_ID, "nubank", "acc-1", _fake_ctx(app)
            )


class TestInitiatePix:
    """Tests for initiate_pix()."""

    @pytest.mark.asyncio
    async def test_initiates_payment_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(initiate_pix)(
            SUBJECT_ID,
            "nubank",
            150.00,
            "recipient@example.com",
            PixKeyType.EMAIL,
            "acc-1",
            "idem-key-1",
            _fake_ctx(app),
        )

        assert result.bank == "nubank"
        assert result.payment.payment_id == "mock-pay-idem-key"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(initiate_pix)(
                SUBJECT_ID,
                "nubank",
                150.00,
                "recipient@example.com",
                PixKeyType.EMAIL,
                "acc-1",
                "idem-key-2",
                _fake_ctx(app),
            )

    @pytest.mark.asyncio
    async def test_repeated_idempotency_key_returns_cached_result(self) -> None:
        """The second call must not hit the adapter again - it should
        return the exact cached result from AppContext.pix_idempotency_cache."""
        app = _app(MockOpenFinanceAdapter("nubank"))

        first = await inspect.unwrap(initiate_pix)(
            SUBJECT_ID,
            "nubank",
            150.00,
            "recipient@example.com",
            PixKeyType.EMAIL,
            "acc-1",
            "idem-key-3",
            _fake_ctx(app),
        )
        second = await inspect.unwrap(initiate_pix)(
            SUBJECT_ID,
            "nubank",
            999.00,  # different amount - proves the cache wins, not a new call
            "someone-else@example.com",
            PixKeyType.EMAIL,
            "acc-1",
            "idem-key-3",
            _fake_ctx(app),
        )

        assert first == second
