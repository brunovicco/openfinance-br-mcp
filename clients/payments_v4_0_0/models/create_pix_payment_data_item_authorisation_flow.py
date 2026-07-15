"""CreatePixPaymentDataItemAuthorisationFlow: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class CreatePixPaymentDataItemAuthorisationFlow(str, Enum):
    CIBA_FLOW = "CIBA_FLOW"
    FIDO_FLOW = "FIDO_FLOW"
    HYBRID_FLOW = "HYBRID_FLOW"

    def __str__(self) -> str:
        return str(self.value)
