"""EnumCreditCardAccountsConsolidationType: enum of possible values (CONSOLIDADO, INDIVIDUAL) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountsConsolidationType(str, Enum):
    CONSOLIDADO = "CONSOLIDADO"
    INDIVIDUAL = "INDIVIDUAL"

    def __str__(self) -> str:
        return str(self.value)
