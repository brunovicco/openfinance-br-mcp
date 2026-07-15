"""Integration tests for MCP tools, resources, and prompts.

Exercises the full protocol path (schema validation, tool execution,
structured content, error translation) using the official in-memory
client/server harness, instead of calling tool functions directly.

A fixed token is injected via ``TokenStore.get_valid_token`` since the
real consent/auth flow is not wired in yet (tracked for Fase 3 of the
production-readiness roadmap) - these tests focus on MCP protocol
behavior, not bank authentication.
"""

import json
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
    Nubank host now, so this doubles as a regression guard for that.

    Explicitly opts into directory_fallback_mode='hardcoded_fallback':
    the default 'fail_closed' (P0.6) would otherwise leave 'nubank' out
    of app.adapters entirely when the mocked Directory resolves to no
    organisations, which is the opposite of what these tests need."""
    monkeypatch.setattr(settings, "environment", "sandbox")
    monkeypatch.setattr(settings, "directory_fallback_mode", "hardcoded_fallback")
    monkeypatch.setattr(settings, "mtls_enabled", False)
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
    """tools/list should return all registered tools with input and output schemas."""
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
        "list_funds",
        "list_variable_incomes",
        "list_treasure_titles",
        "start_consent",
        "complete_consent",
        "check_consent_status",
        "revoke_consent",
        "start_payment_consent",
        "complete_payment_consent",
        "check_payment_consent_status",
    }
    for tool in result.tools:
        assert tool.inputSchema
        assert tool.outputSchema

    start_consent_tool = next(
        tool for tool in result.tools if tool.name == "start_consent"
    )
    assert start_consent_tool.annotations is not None
    assert start_consent_tool.annotations.idempotentHint is False
    scopes_schema = start_consent_tool.inputSchema["properties"]["scopes"]
    assert scopes_schema["minItems"] == 1
    assert set(scopes_schema["items"]["enum"]) == {
        "accounts",
        "balances",
        "transactions",
        "overdraft_limits",
        "credit_card_accounts",
        "credit_card_limits",
        "credit_card_bills",
        "credit_card_transactions",
        "bank_fixed_incomes",
        "funds",
        "variable_incomes",
        "treasure_titles",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("scopes", [[], ["not_a_real_scope"]])
async def test_start_consent_rejects_invalid_scopes_at_protocol_boundary(scopes):
    mcp = build_server()

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=False
    ) as session:
        result = await session.call_tool(
            "start_consent",
            {"subject_id": "12345678900", "bank": "nubank", "scopes": scopes},
        )

    assert result.isError is True
    assert "validation error" in result.content[0].text.lower()


@pytest.mark.asyncio
async def test_resources_expose_current_bank_availability():
    mcp = build_server()

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        listed = await session.list_resources()
        result = await session.read_resource("openfinance://banks/")

    assert [str(resource.uri) for resource in listed.resources] == [
        "openfinance://banks/"
    ]
    payload = json.loads(result.contents[0].text)
    assert payload["environment"] == "mock"
    assert len(payload["banks"]) == 10
    assert all(bank["configured"] is True for bank in payload["banks"])
    assert all(bank["availability"] == "available" for bank in payload["banks"])


@pytest.mark.asyncio
async def test_prompt_renders_monthly_spending_workflow():
    mcp = build_server()

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        listed = await session.list_prompts()
        result = await session.get_prompt(
            "analyze_monthly_spending",
            arguments={
                "bank": "nubank",
                "date_from": "2026-06-01",
                "date_to": "2026-06-30",
                "category": "food",
            },
        )

    assert [prompt.name for prompt in listed.prompts] == ["analyze_monthly_spending"]
    assert "list_transactions" in result.messages[0].content.text
    assert "food" in result.messages[0].content.text


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
async def test_initiate_pix_identical_replay_hits_cache():
    """Two initiate_pix calls with the same idempotency_key AND the same
    payload must not recompute the payment - the second call returns
    the exact cached result (see auth/idempotency_store.py, P2.1)."""
    assert settings.environment == "mock"
    mcp = build_server()
    payload = {
        "subject_id": "12345678900",
        "bank": "nubank",
        "creditor_key_type": "EMAIL",
        "debtor_account_id": "acc_1",
        "idempotency_key": "11111111-1111-1111-1111-111111111111",
        "amount": 10.5,
        "creditor_key": "someone@example.com",
    }

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        first = await session.call_tool("initiate_pix", payload)
        second = await session.call_tool("initiate_pix", payload)

    assert first.isError is False
    assert second.isError is False
    assert first.structuredContent == second.structuredContent


@pytest.mark.asyncio
async def test_initiate_pix_reused_key_different_payload_is_rejected():
    """Reusing an idempotency_key across two *different* payments is a
    client bug the Open Finance Brasil idempotency contract requires
    rejecting outright, not silently returning the unrelated cached
    result for (see auth/idempotency_store.py, P2.1) - contrast with
    test_initiate_pix_identical_replay_hits_cache above."""
    assert settings.environment == "mock"
    mcp = build_server()
    base_payload = {
        "subject_id": "12345678900",
        "bank": "nubank",
        "creditor_key_type": "EMAIL",
        "debtor_account_id": "acc_1",
        "idempotency_key": "33333333-3333-3333-3333-333333333333",
    }

    async with create_connected_server_and_client_session(
        mcp, raise_exceptions=True
    ) as session:
        first = await session.call_tool(
            "initiate_pix",
            {**base_payload, "amount": 10.5, "creditor_key": "someone@example.com"},
        )
        second = await session.call_tool(
            "initiate_pix",
            {
                **base_payload,
                "amount": 999.0,
                "creditor_key": "someone-else@example.com",
            },
        )

    assert first.isError is False
    assert second.isError is True


@pytest.mark.asyncio
async def test_initiate_pix_rejected_outside_mock_without_payment_consent(
    monkeypatch: pytest.MonkeyPatch,
):
    """Outside environment='mock', initiate_pix is no longer blanket-
    disabled (that was P0.9's stopgap) - as of P2.4 it instead requires
    an AUTHORISED payment consent (tools/payments.py) for this subject/
    bank before it will call the bank at all. This fixture's Directory
    mock returns no organisations, so the call actually fails one step
    earlier, at endpoint resolution - but the key regression this
    guards is that the call is *not silently allowed through* to the
    bank the way it would have been if the mock-only gate had simply
    been deleted without adding the payment-consent check in its
    place."""
    monkeypatch.setattr(settings, "environment", "sandbox")
    monkeypatch.setattr(settings, "directory_fallback_mode", "hardcoded_fallback")
    monkeypatch.setattr(settings, "mtls_enabled", False)
    respx_mock = respx.mock()
    respx_mock.start()
    try:
        respx_mock.get(f"{settings.bcb_sandbox_directory_url}participants").mock(
            return_value=httpx.Response(200, json=[])
        )
        mcp = build_server()
        payload = {
            "subject_id": "12345678900",
            "bank": "nubank",
            "amount": 10.5,
            "creditor_key": "someone@example.com",
            "creditor_key_type": "EMAIL",
            "debtor_account_id": "acc_1",
            "idempotency_key": "22222222-2222-2222-2222-222222222222",
        }

        async with create_connected_server_and_client_session(
            mcp, raise_exceptions=False
        ) as session:
            result = await session.call_tool("initiate_pix", payload)

        assert result.isError is True
    finally:
        respx_mock.stop()
