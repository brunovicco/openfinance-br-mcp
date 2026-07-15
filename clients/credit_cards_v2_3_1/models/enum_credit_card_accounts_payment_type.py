"""EnumCreditCardAccountsPaymentType: enum of possible values (A_PRAZO, A_VISTA) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountsPaymentType(str, Enum):
    A_PRAZO = "A_PRAZO"
    A_VISTA = "A_VISTA"

    def __str__(self) -> str:
        return str(self.value)
