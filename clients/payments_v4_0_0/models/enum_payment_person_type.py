"""EnumPaymentPersonType: enum of possible values (PESSOA_JURIDICA, PESSOA_NATURAL) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumPaymentPersonType(str, Enum):
    PESSOA_JURIDICA = "PESSOA_JURIDICA"
    PESSOA_NATURAL = "PESSOA_NATURAL"

    def __str__(self) -> str:
        return str(self.value)
