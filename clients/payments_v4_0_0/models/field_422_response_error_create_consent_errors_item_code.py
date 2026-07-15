"""Field422ResponseErrorCreateConsentErrorsItemCode: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class Field422ResponseErrorCreateConsentErrorsItemCode(str, Enum):
    DATA_PAGAMENTO_INVALIDA = "DATA_PAGAMENTO_INVALIDA"
    DETALHE_PAGAMENTO_INVALIDO = "DETALHE_PAGAMENTO_INVALIDO"
    ERRO_IDEMPOTENCIA = "ERRO_IDEMPOTENCIA"
    FORMA_PAGAMENTO_INVALIDA = "FORMA_PAGAMENTO_INVALIDA"
    NAO_INFORMADO = "NAO_INFORMADO"
    PARAMETRO_INVALIDO = "PARAMETRO_INVALIDO"
    PARAMETRO_NAO_INFORMADO = "PARAMETRO_NAO_INFORMADO"

    def __str__(self) -> str:
        return str(self.value)
