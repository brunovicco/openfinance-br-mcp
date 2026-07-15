"""MCP tools for investments (Fase 4 of Open Finance Brasil).

Exposes ``list_investments`` to query CDBs, LCIs, LCAs, and other bank
fixed-income products, and (P1.3) ``list_funds``,
``list_variable_incomes``, ``list_treasure_titles`` for the three
remaining investment API families - investment funds, exchange-traded
assets (stocks/ETFs), and treasury bonds (Tesouro Direto). All four
follow the same shape: bank + subject_id in, a typed list of positions
plus aggregate gross/net totals out.
"""

from pydantic import BaseModel, Field

from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.investment import (
    BankFixedIncome,
    Fund,
    TreasureTitle,
    VariableIncome,
)
from openfinance_br_mcp.tools.aliases import BankId
from openfinance_br_mcp.tools.errors import translate_errors
from openfinance_br_mcp.tools.principal_guard import require_principal_binding


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
@require_principal_binding
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


class FundListResult(BaseModel):
    """Result of ``list_funds``."""

    bank: BankId
    total_records: int
    summary: InvestmentSummary
    funds: list[Fund] = Field(default_factory=list)


@traced_tool
@translate_errors
@require_principal_binding
async def list_funds(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> FundListResult:
    """Lists a user's investment fund positions via Open Finance Brasil
    Fase 4 (P1.3), including quota quantity/price and gross/net amount.

    Args:
        subject_id: User's CPF.
        bank: Participating bank.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The user's investment funds and aggregate totals.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    fund_list = await adapter.list_funds(subject_id)

    total_gross = sum(float(f.gross_amount) for f in fund_list.data)
    total_net = sum(float(f.net_amount) for f in fund_list.data)

    return FundListResult(
        bank=bank,
        total_records=fund_list.total_records,
        summary=InvestmentSummary(
            total_gross_amount=round(total_gross, 2),
            total_net_amount=round(total_net, 2),
        ),
        funds=fund_list.data,
    )


class VariableIncomeListResult(BaseModel):
    """Result of ``list_variable_incomes``."""

    bank: BankId
    total_records: int
    total_gross_amount: float
    assets: list[VariableIncome] = Field(default_factory=list)


@traced_tool
@translate_errors
@require_principal_binding
async def list_variable_incomes(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> VariableIncomeListResult:
    """Lists a user's variable income asset positions (stocks, ETFs,
    and other exchange-traded assets) via Open Finance Brasil Fase 4
    (P1.3), including quantity, closing price, and gross amount.

    No net_amount is returned here (unlike list_investments/list_funds/
    list_treasure_titles): the real Variable Incomes spec's balance
    data only publishes a gross amount - taxes/fees on these assets are
    reported per-transaction (broker notes), not as a running net
    position.

    Args:
        subject_id: User's CPF.
        bank: Participating bank.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The user's variable income assets and an aggregate gross total.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    asset_list = await adapter.list_variable_incomes(subject_id)

    total_gross = sum(float(a.gross_amount) for a in asset_list.data)

    return VariableIncomeListResult(
        bank=bank,
        total_records=asset_list.total_records,
        total_gross_amount=round(total_gross, 2),
        assets=asset_list.data,
    )


class TreasureTitleListResult(BaseModel):
    """Result of ``list_treasure_titles``."""

    bank: BankId
    total_records: int
    summary: InvestmentSummary
    titles: list[TreasureTitle] = Field(default_factory=list)


@traced_tool
@translate_errors
@require_principal_binding
async def list_treasure_titles(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> TreasureTitleListResult:
    """Lists a user's treasury bond (Tesouro Direto) positions via Open
    Finance Brasil Fase 4 (P1.3), including quantity, updated unit
    price, and gross/net amount.

    Args:
        subject_id: User's CPF.
        bank: Participating bank.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The user's treasury bonds and aggregate totals.
    """
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    title_list = await adapter.list_treasure_titles(subject_id)

    total_gross = sum(float(t.gross_amount) for t in title_list.data)
    total_net = sum(float(t.net_amount) for t in title_list.data)

    return TreasureTitleListResult(
        bank=bank,
        total_records=title_list.total_records,
        summary=InvestmentSummary(
            total_gross_amount=round(total_gross, 2),
            total_net_amount=round(total_net, 2),
        ),
        titles=title_list.data,
    )
