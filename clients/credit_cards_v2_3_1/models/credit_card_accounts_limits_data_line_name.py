"""CreditCardAccountsLimitsDataLineName: a data model of the Credit Cards Accounts API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class CreditCardAccountsLimitsDataLineName(str, Enum):
    CREDITO_A_VISTA = "CREDITO_A_VISTA"
    CREDITO_PARCELADO = "CREDITO_PARCELADO"
    EMPRESTIMO_CARTAO_CONSIGNADO = "EMPRESTIMO_CARTAO_CONSIGNADO"
    OUTROS = "OUTROS"
    SAQUE_CREDITO_BRASIL = "SAQUE_CREDITO_BRASIL"
    SAQUE_CREDITO_EXTERIOR = "SAQUE_CREDITO_EXTERIOR"

    def __str__(self) -> str:
        return str(self.value)
