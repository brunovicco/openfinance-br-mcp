"""MCP tool for fixed-income investments (Fase 4 of Open Finance Brasil).

Exposes ``list_investments`` to query CDBs, LCIs, LCAs, and other
bank fixed-income products.
"""

from pydantic import BaseModel, Field

from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.investment import BankFixedIncome
from openfinance_br_mcp.tools.aliases import BankId
from openfinance_br_mcp.tools.errors import translate_errors


class InvestmentSummary(BaseModel):
    """Aggregate totals across all of a bank's investments."""

    total_gross_amount: float
    total_net_amount: float


class InvestmentListResult(BaseModel):
    """Result of ``list_investments``."""

    bank: BankId
    total_records: int
    summary: InvestmentSummary
    investments: list[BankFixedIncome] = Field(default_factory=list)


@traced_tool
@translate_errors
async def list_investments(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> InvestmentListResult:
    """Lists a user's bank fixed-income investments (CDB, LCI, LCA, RDB)
    via Open Finance Brasil Fase 4, including gross amount, net amount,
    contracted rate, and indexer.

    Args:
        subject_id: User's CPF.
        bank: Participating bank.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The user's fixed-income investments and aggregate totals.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    investment_list = await adapter.list_investments(subject_id)

    total_gross = sum(float(inv.gross_amount) for inv in investment_list.data)
    total_net = sum(float(inv.net_amount) for inv in investment_list.data)

    return InvestmentListResult(
        bank=bank,
        total_records=investment_list.total_records,
        summary=InvestmentSummary(
            total_gross_amount=round(total_gross, 2),
            total_net_amount=round(total_net, 2),
        ),
        investments=investment_list.data,
    )
