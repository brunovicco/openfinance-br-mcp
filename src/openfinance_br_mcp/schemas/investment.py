"""Pydantic schemas for Investments (Fase 4 of Open Finance Brasil).

Covers bank fixed-income products, investment funds, and variable
income per the BCB specification.

Example:
    >>> from openfinance_br_mcp.schemas.investment import BankFixedIncome
"""

from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class InvestmentType(StrEnum):
    """Investment product type. Values are the literal strings defined
    by the Open Finance Brasil spec and must not be translated."""

    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    LCF = "LCF"
    LCI_LCA = "LCI_LCA"
    DEBENTURE = "DEBENTURE"
    CCB = "CCB"
    CRI = "CRI"
    CRA = "CRA"
    RDB = "RDB"


class BankFixedIncome(BaseModel):
    """Bank fixed-income investment.

    Attributes:
        investment_id: Unique investment ID.
        brand_name: Name of the issuing institution.
        investment_type: Product type (CDB, LCI, etc.).
        contracted_rate: Contracted rate (% per year).
        pre_fixed_rate: Pre-fixed rate, if applicable.
        post_fixed_indexer_percentage: % of the post-fixed indexer.
        indexer: Indexer (CDI, IPCA, etc.).
        issue_unit_price: Unit price at issuance.
        issue_date: Issuance date.
        due_date: Maturity date.
        grace_period_date: Grace period end date.
        gross_amount: Current gross amount.
        net_amount: Net amount after income tax.
    """

    investment_id: str
    brand_name: str
    investment_type: InvestmentType
    contracted_rate: Decimal | None = Field(default=None, decimal_places=4)
    pre_fixed_rate: Decimal | None = Field(default=None, decimal_places=4)
    post_fixed_indexer_percentage: Decimal | None = Field(
        default=None, decimal_places=4
    )
    indexer: str | None = None
    issue_unit_price: Decimal | None = Field(default=None, decimal_places=8)
    issue_date: date | None = None
    due_date: date | None = None
    grace_period_date: date | None = None
    gross_amount: Decimal = Field(..., decimal_places=4)
    net_amount: Decimal = Field(..., decimal_places=4)
    currency: str = Field(default="BRL")


class InvestmentList(BaseModel):
    """List of fixed-income investments.

    Attributes:
        data: List of investments.
        total_records: Total available.
    """

    data: list[BankFixedIncome]
    total_records: int = Field(ge=0)


class Fund(BaseModel):
    """Investment fund position (P1.3 - Open Finance Brasil 'funds' family).

    Field shapes verified directly against the generated
    ``clients/funds_v1_1_0`` models rather than assumed: the
    product-list endpoint only ever identifies the fund (brand, CNPJ,
    ANBIMA category) - quota/monetary data lives on the separate
    ``/balances`` endpoint, the same two-call pattern already used for
    ``BankFixedIncome`` (see ``adapters/default_adapter.py::list_funds``).

    Attributes:
        investment_id: Unique investment ID.
        brand_name: Name of the managing institution.
        company_cnpj: CNPJ of the managing institution.
        fund_name: Official name of the fund itself (distinct from
            brand_name, the institution's own name), if published.
        fund_cnpj: CNPJ of the fund itself (distinct from company_cnpj,
            the institution's own CNPJ), if published.
        anbima_category: ANBIMA fund classification (e.g. RENDA_FIXA,
            ACOES), if published.
        quota_quantity: Number of quotas held.
        quota_gross_price_value: Current gross price per quota.
        reference_date: Date this position was last consolidated.
        gross_amount: Current gross value (quota_quantity x quota price).
        net_amount: Value after income/exit taxes.
    """

    investment_id: str
    brand_name: str
    company_cnpj: str
    fund_name: str | None = None
    fund_cnpj: str | None = None
    anbima_category: str | None = None
    quota_quantity: Decimal = Field(..., decimal_places=8)
    quota_gross_price_value: Decimal = Field(..., decimal_places=8)
    reference_date: date | None = None
    gross_amount: Decimal = Field(..., decimal_places=4)
    net_amount: Decimal = Field(..., decimal_places=4)
    currency: str = Field(default="BRL")


class FundList(BaseModel):
    """List of investment fund positions.

    Attributes:
        data: List of funds.
        total_records: Total available.
    """

    data: list[Fund]
    total_records: int = Field(ge=0)


class VariableIncome(BaseModel):
    """Variable income asset position (P1.3 - Open Finance Brasil
    'variable-incomes' family: stocks, ETFs, and similar exchange-traded
    assets).

    Field shapes verified directly against the generated
    ``clients/variable_incomes_v1_3_0`` models. Like Fund/BankFixedIncome,
    identification (ISIN/ticker) and position data (quantity, closing
    price, gross amount) come from two separate endpoints, merged before
    parsing - see ``adapters/default_adapter.py::list_variable_incomes``.

    Attributes:
        investment_id: Unique investment ID.
        brand_name: Name of the custodian institution.
        company_cnpj: CNPJ of the custodian institution.
        isin_code: ISIN code of the asset.
        ticker: Exchange trading ticker (e.g. PETR4).
        quantity: Number of units held.
        closing_price: Closing price on the reference date.
        reference_date: Date this position was last consolidated.
        gross_amount: Current gross value, before taxes/fees.
    """

    investment_id: str
    brand_name: str
    company_cnpj: str
    isin_code: str | None = None
    ticker: str | None = None
    quantity: Decimal = Field(..., decimal_places=8)
    closing_price: Decimal = Field(..., decimal_places=8)
    reference_date: date | None = None
    gross_amount: Decimal = Field(..., decimal_places=4)
    currency: str = Field(default="BRL")


class VariableIncomeList(BaseModel):
    """List of variable income asset positions.

    Attributes:
        data: List of variable income assets.
        total_records: Total available.
    """

    data: list[VariableIncome]
    total_records: int = Field(ge=0)


class TreasureTitle(BaseModel):
    """Treasury bond position (P1.3 - Open Finance Brasil
    'treasure-titles' family, i.e. Tesouro Direto).

    Field shapes verified directly against the generated
    ``clients/treasure_titles_v1_1_0`` models. Product identification
    (ISIN, name, maturity) and position data (quantity, updated price,
    gross/net amount) come from two separate endpoints, merged before
    parsing - see
    ``adapters/default_adapter.py::list_treasure_titles``.

    Attributes:
        investment_id: Unique investment ID.
        brand_name: Name of the custodian institution.
        company_cnpj: CNPJ of the custodian institution.
        isin_code: ISIN code of the title.
        product_name: Title name as listed on tesourodireto.com.br
            (e.g. 'Tesouro Selic 2027').
        due_date: Maturity date.
        purchase_date: Date the client acquired the title.
        quantity: Quantity of titles held.
        updated_unit_price: Current market unit price.
        gross_amount: Current gross value, before taxes/fees.
        net_amount: Value after income tax.
    """

    investment_id: str
    brand_name: str
    company_cnpj: str
    isin_code: str | None = None
    product_name: str | None = None
    due_date: date | None = None
    purchase_date: date | None = None
    quantity: Decimal = Field(..., decimal_places=8)
    updated_unit_price: Decimal = Field(..., decimal_places=8)
    gross_amount: Decimal = Field(..., decimal_places=4)
    net_amount: Decimal = Field(..., decimal_places=4)
    currency: str = Field(default="BRL")


class TreasureTitleList(BaseModel):
    """List of treasury bond positions.

    Attributes:
        data: List of treasury bonds.
        total_records: Total available.
    """

    data: list[TreasureTitle]
    total_records: int = Field(ge=0)
