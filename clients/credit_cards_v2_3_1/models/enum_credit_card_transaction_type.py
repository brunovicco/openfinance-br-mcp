"""EnumCreditCardTransactionType: enum of possible values (CASHBACK, ESTORNO, OPERACOES_CREDITO_CONTRATADAS_CARTAO, OUTROS, PAGAMENTO, TARIFA) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardTransactionType(str, Enum):
    CASHBACK = "CASHBACK"
    ESTORNO = "ESTORNO"
    OPERACOES_CREDITO_CONTRATADAS_CARTAO = "OPERACOES_CREDITO_CONTRATADAS_CARTAO"
    OUTROS = "OUTROS"
    PAGAMENTO = "PAGAMENTO"
    TARIFA = "TARIFA"

    def __str__(self) -> str:
        return str(self.value)
