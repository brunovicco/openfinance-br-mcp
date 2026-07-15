"""EnumRateType: enum of possible values (EXPONENCIAL, LINEAR) for this field, per the Bank Fixed Incomes OpenAPI spec."""

from enum import Enum


class EnumRateType(str, Enum):
    EXPONENCIAL = "EXPONENCIAL"
    LINEAR = "LINEAR"

    def __str__(self) -> str:
        return str(self.value)
