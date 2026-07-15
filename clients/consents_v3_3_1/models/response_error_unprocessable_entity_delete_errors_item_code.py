"""ResponseErrorUnprocessableEntityDeleteErrorsItemCode: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class ResponseErrorUnprocessableEntityDeleteErrorsItemCode(str, Enum):
    CONSENTIMENTO_EM_STATUS_REJEITADO = "CONSENTIMENTO_EM_STATUS_REJEITADO"

    def __str__(self) -> str:
        return str(self.value)
