"""EnumPaymentCancellationStatusType: enum of possible values (CANC) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumPaymentCancellationStatusType(str, Enum):
    CANC = "CANC"

    def __str__(self) -> str:
        return str(self.value)
