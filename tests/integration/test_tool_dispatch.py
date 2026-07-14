"""Integration tests for MCP tool dispatch.

Exercises the full protocol path (schema validation, tool execution,
structured content, error translation) using the official in-memory
client/server harness, instead of calling tool functions directly.

A fixed token is injected via ``TokenStore.get_valid_token`` since the
real consent/auth flow is not wired in yet (tracked for Fase 3 of the
production-readiness roadmap) - these tests focus on MCP protocol
behavior, not bank authentication.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx
from mcp.shared.memory import create_connected_server_and_client_session

from openfinance_br_mcp.adapters.nubank import _NUBANK_BASE
from openfinance_br_mcp.auth.token import TokenResponse
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.server import build_server

FAKE_TOKEN = TokenResponse(
    {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_in": 3600,
        "_obtained_at": datetime.now(UTC),
    }
)


@pytest.fixture
def _fake_token_store():
    with patch(
        "openfinance_br_mcp.auth.token.TokenStore.get_valid_token",
        new=AsyncMock(return_value=FAKE_TOKEN),
    ):
        yield


@pytest.fixture
def _real_adapters(monkeypatch: pytest.MonkeyPatch):
    """Forces environment='sandbox' so build_server() wires real (not
    Mock) adapters, and mocks the Directory of Participants to return
    no organisations - resolution then falls back to each adapter's
    hardcoded default base_url (see context.py), which is what these
    tests' respx routes target. The default's the corrected real
    Nubank host now, so this doubles as a regression guard for that."""
    monkeypatch.setattr(settings, "environment", "sandbox")
    respx.get(f"{settings.bcb_sandbox_directory_url}participants").mock(
        return_value=httpx.Response(200, json=[])
    )


@pytest.mark.asyncio
async def test_mock_mode_list_accounts_works_without_credentials_or_network():
    """environment='mock' (the default) must serve real tool calls with
    zero credentials, zero network access, and zero respx mocking -
    this is this project's primary day-to-day dev loop."""
    assert settings.environment == "mock"  # sanity: exercising the real default
    mcp = build_server()

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        result = await session.call_tool(
            "list_accounts", {"subject_id": "12345678900", "bank": "nubank"}
        )

    assert result.isError is False
    assert result.structuredContent is not None
    assert result.structuredContent["bank"] == "nubank"
    assert len(result.structuredContent["accounts"]) == 1


@pytest.mark.asyncio
async def test_list_tools_returns_all_registered_tools():
    """tools/list should return all 12 tools with input and output schemas."""
    mcp = build_server()

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        result = await session.list_tools()

    names = {tool.name for tool in result.tools}
    assert names == {
        "list_accounts",
        "get_balance",
        "list_transactions",
        "list_credit_cards",
        "get_credit_card_bills",
        "list_pix_keys",
        "initiate_pix",
        "list_investments",
        "start_consent",
        "complete_consent",
        "check_consent_status",
        "revoke_consent",
    }
    for tool in result.tools:
        assert tool.inputSchema
        assert tool.outputSchema


@pytest.mark.asyncio
@respx.mock
async def test_call_list_accounts_returns_structured_content(
    _fake_token_store, _real_adapters, sample_account_response: dict
):
    """A successful list_accounts call should return structuredContent
    matching the schema."""
    respx.get(f"{_NUBANK_BASE}/accounts/v2/accounts").mock(
        return_value=httpx.Response(200, json=sample_account_response)
    )

    mcp = build_server()
    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        result = await session.call_tool(
            "list_accounts", {"subject_id": "12345678900", "bank": "nubank"}
        )

    assert result.isError is False
    assert result.structuredContent is not None
    assert result.structuredContent["bank"] == "nubank"
    assert result.structuredContent["total_records"] == 1
    assert len(result.structuredContent["accounts"]) == 1


@pytest.mark.asyncio
async def test_call_tool_with_unknown_bank_is_rejected_by_schema():
    """``bank`` is a schema-validated Literal, so an unknown value is
    rejected at the protocol layer before the tool body ever runs -
    surfaced as a tool error, not a domain exception leaking out."""
    mcp = build_server()
    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=False
    ) as session:
        result = await session.call_tool(
            "get_balance",
            {"subject_id": "12345678900", "bank": "unknown_bank", "account_id": "x"},
        )

    assert result.isError is True


@pytest.mark.asyncio
@respx.mock
async def test_initiate_pix_idempotent_replay_hits_cache(
    _fake_token_store, _real_adapters
):
    """Two initiate_pix calls with the same idempotency_key must not
    call the bank twice."""
    route = respx.post(f"{_NUBANK_BASE}/payments/v4/pix/payments").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {"paymentId": "pay_1", "status": "ACSP", "endToEndId": "e2e_1"}
            },
        )
    )

    mcp = build_server()
    payload = {
        "subject_id": "12345678900",
        "bank": "nubank",
        "amount": 10.5,
        "creditor_key": "someone@example.com",
        "creditor_key_type": "EMAIL",
        "debtor_account_id": "acc_1",
        "idempotency_key": "11111111-1111-1111-1111-111111111111",
    }

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        first = await session.call_tool("initiate_pix", payload)
        second = await session.call_tool("initiate_pix", payload)

    assert first.isError is False
    assert second.isError is False
    assert first.structuredContent == second.structuredContent
    assert route.call_count == 1
