"""EnumCreditCardAccountsLineLimitType: enum of possible values (LIMITE_CREDITO_MODALIDADE_OPERACAO, LIMITE_CREDITO_TOTAL) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountsLineLimitType(str, Enum):
    LIMITE_CREDITO_MODALIDADE_OPERACAO = "LIMITE_CREDITO_MODALIDADE_OPERACAO"
    LIMITE_CREDITO_TOTAL = "LIMITE_CREDITO_TOTAL"

    def __str__(self) -> str:
        return str(self.value)
