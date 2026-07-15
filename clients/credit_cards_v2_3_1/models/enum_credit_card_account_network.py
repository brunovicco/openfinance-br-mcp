"""EnumCreditCardAccountNetwork: enum of possible values (AMERICAN_EXPRESS, BANDEIRA_PROPRIA, CHEQUE_ELETRONICO, DINERS_CLUB, ELO, HIPERCARD, ...) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountNetwork(str, Enum):
    AMERICAN_EXPRESS = "AMERICAN_EXPRESS"
    BANDEIRA_PROPRIA = "BANDEIRA_PROPRIA"
    CHEQUE_ELETRONICO = "CHEQUE_ELETRONICO"
    DINERS_CLUB = "DINERS_CLUB"
    ELO = "ELO"
    HIPERCARD = "HIPERCARD"
    MASTERCARD = "MASTERCARD"
    OUTRAS = "OUTRAS"
    VISA = "VISA"

    def __str__(self) -> str:
        return str(self.value)
