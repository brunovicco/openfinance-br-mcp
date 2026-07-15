"""EnumFundsTransactionsCurrentType: enum of possible values (ENTRADA, SAIDA) for this field, per the Funds OpenAPI spec."""

from enum import Enum


class EnumFundsTransactionsCurrentType(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

    def __str__(self) -> str:
        return str(self.value)
