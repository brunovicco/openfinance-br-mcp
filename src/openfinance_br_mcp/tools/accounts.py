"""MCP tools for bank account operations.

Exposes ``list_accounts`` and ``get_balance``, which Claude can invoke
to query accounts and balances at any participating institution.
"""

from pydantic import BaseModel

from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.account import Account, AccountBalance
from openfinance_br_mcp.tools.aliases import BankId
from openfinance_br_mcp.tools.errors import translate_errors


class AccountListResult(BaseModel):
    """Result of ``list_accounts``."""

    bank: BankId
    total_records: int
    accounts: list[Account]


class BalanceResult(BaseModel):
    """Result of ``get_balance``."""

    bank: BankId
    balance: AccountBalance


@traced_tool
@translate_errors
async def list_accounts(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> AccountListResult:
    """Lists all bank accounts (checking, savings, prepaid) of a user
    at an institution participating in Open Finance Brasil.

    Args:
        subject_id: User's CPF (digits only) or internal ID.
        bank: Identifier of the participating bank.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The user's accounts at the given bank.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    account_list = await adapter.get_accounts(subject_id)
    return AccountListResult(
        bank=bank,
        total_records=account_list.total_records,
        accounts=account_list.data,
    )


@traced_tool
@translate_errors
async def get_balance(
    subject_id: str, bank: BankId, account_id: str, ctx: AppRequestContext
) -> BalanceResult:
    """Returns the available, blocked, and automatically invested balance
    of a specific bank account on Open Finance Brasil.

    Args:
        subject_id: User's CPF.
        bank: Identifier of the participating bank.
        account_id: Account ID returned by list_accounts.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The account's current balance.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    balance = await adapter.get_balance(subject_id, account_id)
    return BalanceResult(bank=bank, balance=balance)
