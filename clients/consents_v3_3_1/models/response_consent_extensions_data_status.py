"""ResponseConsentExtensionsDataStatus: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class ResponseConsentExtensionsDataStatus(str, Enum):
    AUTHORISED = "AUTHORISED"
    AWAITING_AUTHORISATION = "AWAITING_AUTHORISATION"
    REJECTED = "REJECTED"

    def __str__(self) -> str:
        return str(self.value)
