"""ResponseConsentReadDataRejectionReasonCode: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class ResponseConsentReadDataRejectionReasonCode(str, Enum):
    CONSENT_EXPIRED = "CONSENT_EXPIRED"
    CONSENT_MAX_DATE_REACHED = "CONSENT_MAX_DATE_REACHED"
    CONSENT_TECHNICAL_ISSUE = "CONSENT_TECHNICAL_ISSUE"
    CUSTOMER_MANUALLY_REJECTED = "CUSTOMER_MANUALLY_REJECTED"
    CUSTOMER_MANUALLY_REVOKED = "CUSTOMER_MANUALLY_REVOKED"
    INTERNAL_SECURITY_REASON = "INTERNAL_SECURITY_REASON"

    def __str__(self) -> str:
        return str(self.value)
