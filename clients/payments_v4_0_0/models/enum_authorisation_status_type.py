"""EnumAuthorisationStatusType: enum of possible values (AUTHORISED, AWAITING_AUTHORISATION, CONSUMED, PARTIALLY_ACCEPTED, REJECTED) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumAuthorisationStatusType(str, Enum):
    AUTHORISED = "AUTHORISED"
    AWAITING_AUTHORISATION = "AWAITING_AUTHORISATION"
    CONSUMED = "CONSUMED"
    PARTIALLY_ACCEPTED = "PARTIALLY_ACCEPTED"
    REJECTED = "REJECTED"

    def __str__(self) -> str:
        return str(self.value)
