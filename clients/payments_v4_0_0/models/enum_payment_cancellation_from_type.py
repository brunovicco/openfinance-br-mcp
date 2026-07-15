"""EnumPaymentCancellationFromType: enum of possible values (DETENTORA, INICIADORA) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumPaymentCancellationFromType(str, Enum):
    DETENTORA = "DETENTORA"
    INICIADORA = "INICIADORA"

    def __str__(self) -> str:
        return str(self.value)
