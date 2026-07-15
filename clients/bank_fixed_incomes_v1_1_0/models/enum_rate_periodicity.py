"""EnumRatePeriodicity: enum of possible values (ANUAL, DIARIO, MENSAL, SEMESTRAL) for this field, per the Bank Fixed Incomes OpenAPI spec."""

from enum import Enum


class EnumRatePeriodicity(str, Enum):
    ANUAL = "ANUAL"
    DIARIO = "DIARIO"
    MENSAL = "MENSAL"
    SEMESTRAL = "SEMESTRAL"

    def __str__(self) -> str:
        return str(self.value)
