"""MCP tools for credit cards (Fase 2 of Open Finance Brasil).

Exposes ``list_credit_cards`` to list card accounts and
``get_credit_card_bills`` to query bills.
"""

from pydantic import BaseModel

from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.credit_card import Bill, CreditCardAccount
from openfinance_br_mcp.tools.aliases import BankId
from openfinance_br_mcp.tools.errors import translate_errors
from openfinance_br_mcp.tools.principal_guard import require_principal_binding


class CreditCardListResult(BaseModel):
    """Result of ``list_credit_cards``."""

    bank: BankId
    credit_cards: list[CreditCardAccount]


class BillListResult(BaseModel):
    """Result of ``get_credit_card_bills``."""

    bank: BankId
    credit_card_account_id: str
    bills: list[Bill]


@traced_tool
@translate_errors
@require_principal_binding
async def list_credit_cards(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> CreditCardListResult:
    """Lists all credit card accounts of a user at an institution
    participating in Open Finance Brasil, including available and
    total credit limit.

    Args:
        subject_id: User's CPF.
        bank: Identifier of the participating bank.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The user's credit card accounts at the given bank.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    cards = await adapter.get_credit_card_accounts(subject_id)
    return CreditCardListResult(bank=bank, credit_cards=cards)


@traced_tool
@translate_errors
@require_principal_binding
async def get_credit_card_bills(
    subject_id: str, bank: BankId, credit_card_account_id: str, ctx: AppRequestContext
) -> BillListResult:
    """Returns the bills (open and past) of a credit card via Open
    Finance Brasil, including total amount, minimum payment, and due date.

    Args:
        subject_id: User's CPF.
        bank: Identifier of the participating bank.
        credit_card_account_id: ID returned by list_credit_cards.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The bills of the given credit card account.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    bills = await adapter.get_credit_card_bills(subject_id, credit_card_account_id)
    return BillListResult(
        bank=bank, credit_card_account_id=credit_card_account_id, bills=bills
    )
