"""EnumCreditDebitIndicator: enum of possible values (CREDITO, DEBITO) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditDebitIndicator(str, Enum):
    CREDITO = "CREDITO"
    DEBITO = "DEBITO"

    def __str__(self) -> str:
        return str(self.value)
