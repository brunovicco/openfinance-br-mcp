"""EnumAccountPaymentsType: enum of possible values (CACC, SVGS, TRAN) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumAccountPaymentsType(str, Enum):
    CACC = "CACC"
    SVGS = "SVGS"
    TRAN = "TRAN"

    def __str__(self) -> str:
        return str(self.value)
