"""Unit tests for the translate_errors decorator."""

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.tools.errors import translate_errors


@translate_errors
async def _raises_domain_error() -> str:
    raise ValidationError('Bank "acme" is not available.', code="UNKNOWN_BANK")


@translate_errors
async def _raises_unexpected_error() -> str:
    raise RuntimeError("boom")


@translate_errors
async def _succeeds() -> str:
    return "ok"


class TestTranslateErrors:
    """Tests for translate_errors' domain-to-ToolError translation."""

    @pytest.mark.asyncio
    async def test_domain_error_is_translated_to_tool_error(self) -> None:
        """An OpenFinanceError subclass must become a ToolError with its message."""
        with pytest.raises(ToolError, match='Bank "acme" is not available.'):
            await _raises_domain_error()

    @pytest.mark.asyncio
    async def test_unexpected_error_is_left_to_propagate(self) -> None:
        """Non-domain exceptions are not swallowed or wrapped here - FastMCP
        itself is responsible for turning them into a tool error response."""
        with pytest.raises(RuntimeError, match="boom"):
            await _raises_unexpected_error()

    @pytest.mark.asyncio
    async def test_successful_call_passes_through(self) -> None:
        """A function that doesn't raise should behave transparently."""
        assert await _succeeds() == "ok"
