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
