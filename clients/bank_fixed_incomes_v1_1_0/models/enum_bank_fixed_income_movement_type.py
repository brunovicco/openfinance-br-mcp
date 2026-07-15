"""EnumBankFixedIncomeMovementType: enum of possible values (ENTRADA, SAIDA) for this field, per the Bank Fixed Incomes OpenAPI spec."""

from enum import Enum


class EnumBankFixedIncomeMovementType(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

    def __str__(self) -> str:
        return str(self.value)
