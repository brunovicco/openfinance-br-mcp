"""EnumPaymentStatusType: enum of possible values (ACCP, ACPD, ACSC, CANC, PDNG, RCVD, ...) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumPaymentStatusType(str, Enum):
    ACCP = "ACCP"
    ACPD = "ACPD"
    ACSC = "ACSC"
    CANC = "CANC"
    PDNG = "PDNG"
    RCVD = "RCVD"
    RJCT = "RJCT"
    SCHD = "SCHD"

    def __str__(self) -> str:
        return str(self.value)
