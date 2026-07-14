"""Pydantic schemas for the Transactions resource.

Models the account statement per the BCB specification for Fase 2
of Open Finance Brasil.

Example:
    >>> from openfinance_br_mcp.schemas.transaction import Transaction
    >>> tx = Transaction(
    ...     transaction_id="tx1",
    ...     completed_authorised_payment_type="DEBITO",
    ...     credit_debit_type="DEBITO",
    ...     transaction_name="PURCHASE",
    ...     type="PIX",
    ...     amount=Decimal("100.00"),
    ...     transaction_date=date.today(),
    ... )
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class CreditDebitType(StrEnum):
    """Indicates whether the transaction is a credit or a debit. Values
    are the literal strings defined by the Open Finance Brasil spec
    and must not be translated."""

    CREDITO = "CREDITO"
    DEBITO = "DEBITO"


class TransactionType(StrEnum):
    """Transaction type per the BCB enum. Values are the literal strings
    defined by the Open Finance Brasil spec and must not be translated."""

    TED = "TED"
    DOC = "DOC"
    PIX = "PIX"
    TRANSFERENCIA_MESMA_INSTITUICAO = "TRANSFERENCIA_MESMA_INSTITUICAO"
    BOLETO = "BOLETO"
    CONVENIO_ARRECADACAO = "CONVENIO_ARRECADACAO"
    PACOTE_TARIFA_SERVICOS = "PACOTE_TARIFA_SERVICOS"
    TARIFA_SERVICOS_AVULSOS = "TARIFA_SERVICOS_AVULSOS"
    FOLHA_PAGAMENTO = "FOLHA_PAGAMENTO"
    DEPOSITO = "DEPOSITO"
    SAQUE = "SAQUE"
    CARTAO = "CARTAO"
    ENCARGOS_JUROS_CHEQUE_ESPECIAL = "ENCARGOS_JUROS_CHEQUE_ESPECIAL"
    RENDIMENTO_APLIC_FINANCEIRA = "RENDIMENTO_APLIC_FINANCEIRA"
    PORTABILIDADE_SALARIO = "PORTABILIDADE_SALARIO"
    RESGATE_APLIC_FINANCEIRA = "RESGATE_APLIC_FINANCEIRA"
    OPERACAO_CREDITO = "OPERACAO_CREDITO"
    OUTROS = "OUTROS"


class PaymentType(StrEnum):
    """Type of the authorized payment. Values are the literal strings
    defined by the Open Finance Brasil spec and must not be translated."""

    DEBITO = "DEBITO"
    CREDITO = "CREDITO"


class Transaction(BaseModel):
    """Represents a transaction in a checking account statement.

    Attributes:
        transaction_id: Unique transaction identifier.
        completed_authorised_payment_type: Type of the settled payment.
        credit_debit_type: Whether it's a debit or credit to the account.
        transaction_name: Description/name of the transaction.
        type: Transaction type (PIX, TED, CARTAO, etc.).
        amount: Transaction amount.
        transaction_currency: Transaction currency.
        transaction_date: Settlement date.
        transaction_datetime: Date and time, when available.
        counterpart_name: Name of the counterparty.
        counterpart_cpf_cnpj: CPF/CNPJ of the counterparty (masked).
        category: Inferred category (filled in by the DSPy module).
    """

    transaction_id: str = Field(..., description="Unique transaction ID")
    completed_authorised_payment_type: PaymentType
    credit_debit_type: CreditDebitType
    transaction_name: str = Field(..., max_length=200)
    type: TransactionType
    amount: Decimal = Field(..., decimal_places=4)
    transaction_currency: str = Field(default="BRL")
    transaction_date: date
    transaction_datetime: datetime | None = None
    counterpart_name: str | None = None
    counterpart_cpf_cnpj: str | None = Field(
        default=None, description="Masked CPF/CNPJ of the counterparty"
    )
    category: str | None = Field(
        default=None, description="DSPy category: food, transport, utilities, etc."
    )


class TransactionFilters(BaseModel):
    """Filters for listing transactions.

    Attributes:
        account_id: ID of the account to query (required).
        date_from: Start date of the period (YYYY-MM-DD).
        date_to: End date of the period (YYYY-MM-DD).
        credit_debit_type: Restrict to debits or credits only.
        page: Page number (1-based).
        page_size: Records per page (max 1000).
    """

    account_id: str
    date_from: date | None = None
    date_to: date | None = None
    credit_debit_type: CreditDebitType | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=1000)


class TransactionList(BaseModel):
    """Paginated list of transactions.

    Attributes:
        data: List of transactions.
        total_records: Total available for the applied filter.
        total_pages: Total number of pages.
    """

    data: list[Transaction]
    total_records: int = Field(ge=0)
    total_pages: int = Field(ge=0)
