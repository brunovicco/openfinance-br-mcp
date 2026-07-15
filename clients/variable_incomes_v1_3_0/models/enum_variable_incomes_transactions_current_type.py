"""EnumVariableIncomesTransactionsCurrentType: enum of possible values (ENTRADA, SAIDA) for this field, per the Variable Incomes OpenAPI spec."""

from enum import Enum


class EnumVariableIncomesTransactionsCurrentType(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

    def __str__(self) -> str:
        return str(self.value)
