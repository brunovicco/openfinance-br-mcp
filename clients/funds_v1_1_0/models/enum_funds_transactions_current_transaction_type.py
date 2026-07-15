"""EnumFundsTransactionsCurrentTransactionType: enum of possible values (AMORTIZACAO, APLICACAO, COME_COTAS, OUTROS, RESGATE, TRANSFERENCIA_COTAS) for this field, per the Funds OpenAPI spec."""

from enum import Enum


class EnumFundsTransactionsCurrentTransactionType(str, Enum):
    AMORTIZACAO = "AMORTIZACAO"
    APLICACAO = "APLICACAO"
    COME_COTAS = "COME_COTAS"
    OUTROS = "OUTROS"
    RESGATE = "RESGATE"
    TRANSFERENCIA_COTAS = "TRANSFERENCIA_COTAS"

    def __str__(self) -> str:
        return str(self.value)
