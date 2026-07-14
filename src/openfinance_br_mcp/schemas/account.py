"""Pydantic schemas for the Accounts resource.

Models the Fase 2 resources of Open Finance Brasil as specified by
the Banco Central:
https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/17367790

Example:
    >>> from openfinance_br_mcp.schemas.account import Account, AccountBalance
    >>> account = Account(account_id="abc", branch="0001", number="12345-6",
    ...                   type="CONTA_DEPOSITO_A_VISTA", subtype="INDIVIDUAL",
    ...                   currency="BRL")
"""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class AccountType(StrEnum):
    """Account types per the BCB enum. Values are the literal strings
    defined by the Open Finance Brasil spec and must not be translated."""

    CONTA_DEPOSITO_A_VISTA = "CONTA_DEPOSITO_A_VISTA"
    CONTA_POUPANCA = "CONTA_POUPANCA"
    CONTA_PAGAMENTO_PRE_PAGA = "CONTA_PAGAMENTO_PRE_PAGA"


class AccountSubType(StrEnum):
    """Account subtype. Values are the literal strings defined by the
    Open Finance Brasil spec and must not be translated."""

    INDIVIDUAL = "INDIVIDUAL"
    CONJUNTA_SIMPLES = "CONJUNTA_SIMPLES"
    CONJUNTA_SOLIDARIA = "CONJUNTA_SOLIDARIA"


class Account(BaseModel):
    """Represents a bank account returned by Open Finance.

    Attributes:
        account_id: Unique account identifier at the institution.
        branch: Branch code (4 digits).
        number: Account number with check digit.
        check_digit: Separate check digit, when available.
        type: Account type (CONTA_DEPOSITO_A_VISTA, etc.).
        subtype: Account subtype.
        currency: ISO 4217 currency code (e.g. 'BRL').
        compe_code: 3-digit COMPE code of the institution.
        ispb_code: 8-digit ISPB code of the institution.
    """

    account_id: str = Field(..., description="Unique account ID at the institution")
    branch: str = Field(..., min_length=4, max_length=4, description="Branch code")
    number: str = Field(..., description="Account number with check digit")
    check_digit: str | None = Field(default=None, description="Check digit")
    type: AccountType = Field(..., description="Account type")
    subtype: AccountSubType = Field(..., description="Account subtype")
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    compe_code: str | None = Field(default=None, description="3-digit COMPE code")
    ispb_code: str | None = Field(default=None, description="8-digit ISPB code")


class AccountBalance(BaseModel):
    """Balance of an account at a given point in time.

    Attributes:
        account_id: Associated account ID.
        available_amount: Balance available for use.
        blocked_amount: Blocked balance (holds, garnishments, etc.).
        automatically_invested_amount: Amount in automatic investment.
        overdraft_contracted_limit: Contracted overdraft limit.
        overdraft_used_limit: Used overdraft limit.
        unarranged_overdraft_amount: Unarranged overdraft amount used.
        currency: ISO 4217 currency code.
    """

    account_id: str
    available_amount: Decimal = Field(..., decimal_places=4)
    blocked_amount: Decimal = Field(default=Decimal("0"), decimal_places=4)
    automatically_invested_amount: Decimal = Field(
        default=Decimal("0"), decimal_places=4
    )
    overdraft_contracted_limit: Decimal | None = Field(default=None, decimal_places=4)
    overdraft_used_limit: Decimal | None = Field(default=None, decimal_places=4)
    unarranged_overdraft_amount: Decimal | None = Field(default=None, decimal_places=4)
    currency: str = Field(default="BRL")


class AccountList(BaseModel):
    """Paginated list of accounts.

    Attributes:
        data: List of returned accounts.
        total_records: Total number of records available.
        total_pages: Total number of pages available.
    """

    data: list[Account]
    total_records: int = Field(ge=0)
    total_pages: int = Field(ge=0)
