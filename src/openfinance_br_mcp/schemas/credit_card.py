"""Pydantic schemas for Credit Cards.

Models card, bill, and transaction data structures per the BCB
Fase 2 - Credit Cards API specification.

Example:
    >>> from openfinance_br_mcp.schemas.credit_card import CreditCardAccount, Bill
"""

from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class CreditCardNetwork(StrEnum):
    """Credit card network/brand. Values are the literal strings defined
    by the Open Finance Brasil spec and must not be translated."""

    MASTERCARD = "MASTERCARD"
    VISA = "VISA"
    ELO = "ELO"
    AMEX = "AMEX"
    HIPERCARD = "HIPERCARD"
    DINERS = "DINERS"
    OUTROS = "OUTROS"


class CreditCardAccount(BaseModel):
    """Credit card account.

    Attributes:
        credit_card_account_id: Unique ID of the card account.
        brand_name: Name of the issuing bank.
        company_cnpj: CNPJ of the card-issuing company.
        name: Name of the card product.
        product_type: Product type (e.g. CREDITO_A_VISTA).
        credit_card_network: Card network/brand.
        available_credit_limit: Available credit limit.
        total_credit_limit: Total credit limit.
    """

    credit_card_account_id: str
    brand_name: str
    company_cnpj: str | None = None
    name: str
    product_type: str | None = None
    credit_card_network: CreditCardNetwork
    available_credit_limit: Decimal | None = Field(default=None, decimal_places=4)
    total_credit_limit: Decimal | None = Field(default=None, decimal_places=4)
    currency: str = Field(default="BRL")


class Bill(BaseModel):
    """Credit card bill.

    Attributes:
        bill_id: Bill ID.
        due_date: Due date.
        bill_total_amount: Total amount of the bill.
        bill_minimum_amount: Minimum payment amount.
        is_installment: Whether the bill includes installments.
        finance_charges: Finance charges applied.
    """

    bill_id: str
    due_date: date
    bill_total_amount: Decimal = Field(..., decimal_places=4)
    bill_minimum_amount: Decimal = Field(..., decimal_places=4)
    is_installment: bool = False
    finance_charges: Decimal = Field(default=Decimal("0"), decimal_places=4)
    currency: str = Field(default="BRL")
