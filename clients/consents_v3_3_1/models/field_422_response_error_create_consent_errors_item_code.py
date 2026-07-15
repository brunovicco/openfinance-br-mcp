"""Field422ResponseErrorCreateConsentErrorsItemCode: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class Field422ResponseErrorCreateConsentErrorsItemCode(str, Enum):
    DATA_EXPIRACAO_INVALIDA = "DATA_EXPIRACAO_INVALIDA"
    DEPENDE_MULTIPLA_ALCADA = "DEPENDE_MULTIPLA_ALCADA"
    ERRO_NAO_MAPEADO = "ERRO_NAO_MAPEADO"
    ESTADO_CONSENTIMENTO_INVALIDO = "ESTADO_CONSENTIMENTO_INVALIDO"

    def __str__(self) -> str:
        return str(self.value)
