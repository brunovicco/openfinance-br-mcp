"""Pydantic schemas for PIX - keys and payments.

Covers querying registered keys and initiating PIX payments, per
Fase 3 of Open Finance Brasil.

Example:
    >>> from openfinance_br_mcp.schemas.pix import PixKey, PixPayment
"""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

CanonicalAmount = Annotated[
    str,
    Field(
        pattern=r"^\d+\.\d{2}$",
        description="BRL amount serialized with exactly two decimal places.",
    ),
]


class PixKeyType(StrEnum):
    """PIX key type. Values are the literal strings defined by the
    Open Finance Brasil spec and must not be translated."""

    CPF = "CPF"
    CNPJ = "CNPJ"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    EVP = "EVP"


class PixPaymentStatus(StrEnum):
    """Status of an initiated PIX payment. Values are the literal
    strings defined by the Open Finance Brasil spec and must not be
    translated."""

    RCVD = "RCVD"  # Received for asynchronous processing
    ACCP = "ACCP"  # Accepted customer profile
    ACPD = "ACPD"  # Accepted technical validation
    PDNG = "PDNG"  # Pending
    ACSC = "ACSC"  # Completed successfully
    RJCT = "RJCT"  # Rejected
    CANC = "CANC"  # Cancelled
    SCHD = "SCHD"  # Scheduled


class PixKey(BaseModel):
    """PIX key registered to an account.

    Attributes:
        key: Key value (CPF, email, phone, or EVP).
        key_type: Type of the key.
        account_id: ID of the account linked to the key.
        created_at: Date the key was registered.
    """

    key: str = Field(..., description="PIX key value")
    key_type: PixKeyType
    account_id: str
    created_at: datetime | None = None


class PixPaymentRequest(BaseModel):
    """Data needed to initiate a PIX payment.

    Attributes:
        amount: Payment amount in BRL.
        creditor_key: PIX key of the recipient.
        creditor_key_type: Type of the recipient's key.
        debtor_account_id: Payer's account.
        description: Payment description/reason (QR code note).
        idempotency_key: Idempotency key to avoid duplicates.
        consent_id: Payment consent authorizing this exact request.
    """

    amount: Decimal = Field(..., decimal_places=2, gt=Decimal("0"))
    creditor_key: str
    creditor_key_type: PixKeyType
    debtor_account_id: str
    description: str = Field(default="", max_length=140)
    idempotency_key: str = Field(
        ..., description="Client-generated UUID for idempotency"
    )
    consent_id: str | None = Field(
        default=None,
        description="Required outside mock mode; identifies the payment journey.",
    )


class PixPayment(BaseModel):
    """Result of a PIX payment initiation.

    Attributes:
        payment_id: Payment ID at the initiating institution.
        status: Current status of the payment.
        amount: Payment amount.
        end_to_end_id: End-to-end identifier assigned by the Central Bank.
        created_at: Creation timestamp.
    """

    payment_id: str
    status: PixPaymentStatus
    amount: Decimal
    end_to_end_id: str | None = None
    created_at: datetime
