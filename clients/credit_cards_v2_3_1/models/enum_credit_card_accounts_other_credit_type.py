"""EnumCreditCardAccountsOtherCreditType: enum of possible values (CREDITO_ROTATIVO, EMPRESTIMO, OUTROS, PARCELAMENTO_FATURA) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountsOtherCreditType(str, Enum):
    CREDITO_ROTATIVO = "CREDITO_ROTATIVO"
    EMPRESTIMO = "EMPRESTIMO"
    OUTROS = "OUTROS"
    PARCELAMENTO_FATURA = "PARCELAMENTO_FATURA"

    def __str__(self) -> str:
        return str(self.value)
