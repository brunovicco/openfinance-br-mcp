"""ResponseFundsProductIdentificationDataAnbimaCategory: a data model of the Funds API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class ResponseFundsProductIdentificationDataAnbimaCategory(str, Enum):
    ACOES = "ACOES"
    CAMBIAL = "CAMBIAL"
    MULTIMERCADO = "MULTIMERCADO"
    RENDA_FIXA = "RENDA_FIXA"

    def __str__(self) -> str:
        return str(self.value)
