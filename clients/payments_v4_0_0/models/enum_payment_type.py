"""EnumPaymentType: enum of possible values (PIX) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumPaymentType(str, Enum):
    PIX = "PIX"

    def __str__(self) -> str:
        return str(self.value)
