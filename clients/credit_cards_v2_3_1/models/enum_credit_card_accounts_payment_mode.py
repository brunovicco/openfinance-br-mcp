"""EnumCreditCardAccountsPaymentMode: enum of possible values (AVERBACAO_FOLHA, BOLETO_BANCARIO, DEBITO_CONTA_CORRENTE, PIX) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountsPaymentMode(str, Enum):
    AVERBACAO_FOLHA = "AVERBACAO_FOLHA"
    BOLETO_BANCARIO = "BOLETO_BANCARIO"
    DEBITO_CONTA_CORRENTE = "DEBITO_CONTA_CORRENTE"
    PIX = "PIX"

    def __str__(self) -> str:
        return str(self.value)
