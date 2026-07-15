"""EnumRejectedBy: enum of possible values (ASPSP, TPP, USER) for this field, per the Consents OpenAPI spec."""

from enum import Enum


class EnumRejectedBy(str, Enum):
    ASPSP = "ASPSP"
    TPP = "TPP"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
