"""EnumCalculation: enum of possible values (DIAS_CORRIDOS, DIAS_UTEIS) for this field, per the Bank Fixed Incomes OpenAPI spec."""

from enum import Enum


class EnumCalculation(str, Enum):
    DIAS_CORRIDOS = "DIAS_CORRIDOS"
    DIAS_UTEIS = "DIAS_UTEIS"

    def __str__(self) -> str:
        return str(self.value)
