"""MCP tool for listing and categorizing bank transactions.

Exposes ``list_transactions``, which combines the Open Finance
statement with automatic categorization via DSPy. Categorization is
optional and only enabled when ``categorize=true`` is passed in the
arguments.
"""

from datetime import date

from pydantic import BaseModel

from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.transaction import (
    CreditDebitType,
    Transaction,
    TransactionFilters,
)
from openfinance_br_mcp.tools.aliases import BankId
from openfinance_br_mcp.tools.errors import translate_errors


class TransactionListResult(BaseModel):
    """Result of ``list_transactions``."""

    bank: BankId
    total_records: int
    total_pages: int
    categorized: bool
    transactions: list[Transaction]


@traced_tool
@translate_errors
async def list_transactions(
    subject_id: str,
    bank: BankId,
    account_id: str,
    ctx: AppRequestContext,
    date_from: date | None = None,
    date_to: date | None = None,
    credit_debit_type: CreditDebitType | None = None,
    page: int = 1,
    page_size: int = 100,
    categorize: bool = False,
) -> TransactionListResult:
    """Returns the bank statement of an account on Open Finance Brasil
    with date and type filters. Supports automatic transaction
    categorization via AI (categorize=true, requires ANTHROPIC_API_KEY).

    Args:
        subject_id: User's CPF.
        bank: Identifier of the participating bank.
        account_id: Account ID returned by list_accounts.
        ctx: MCP request context, providing access to shared adapters
            and the categorizer.
        date_from: Start date of the period.
        date_to: End date of the period.
        credit_debit_type: Restrict to credits or debits only.
        page: Page number (1-based).
        page_size: Records per page (1-1000).
        categorize: If true, categorizes each transaction via AI.

    Returns:
        The account's transactions for the requested period.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    filters = TransactionFilters(
        account_id=account_id,
        date_from=date_from,
        date_to=date_to,
        credit_debit_type=credit_debit_type,
        page=page,
        page_size=page_size,
    )

    tx_list = await adapter.list_transactions(subject_id, filters)

    if categorize and tx_list.data:
        pairs = [
            (
                tx.transaction_name,
                float(tx.amount)
                * (-1 if tx.credit_debit_type == CreditDebitType.DEBITO else 1),
            )
            for tx in tx_list.data
        ]
        categories = await app.categorizer.categorize_batch(pairs)
        for tx, (cat, _conf) in zip(tx_list.data, categories, strict=True):
            tx.category = cat

    return TransactionListResult(
        bank=bank,
        total_records=tx_list.total_records,
        total_pages=tx_list.total_pages,
        categorized=categorize,
        transactions=tx_list.data,
    )
