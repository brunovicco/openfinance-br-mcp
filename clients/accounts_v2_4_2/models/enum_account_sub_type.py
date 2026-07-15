"""EnumAccountSubType: enum of possible values (CONJUNTA_SIMPLES, CONJUNTA_SOLIDARIA, INDIVIDUAL) for this field, per the Accounts OpenAPI spec."""

from enum import Enum


class EnumAccountSubType(str, Enum):
    CONJUNTA_SIMPLES = "CONJUNTA_SIMPLES"
    CONJUNTA_SOLIDARIA = "CONJUNTA_SOLIDARIA"
    INDIVIDUAL = "INDIVIDUAL"

    def __str__(self) -> str:
        return str(self.value)
