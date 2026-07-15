"""EnumCreditCardAccountsBillingValueType: enum of possible values (OUTRO_VALOR_PAGO_FATURA, VALOR_PAGAMENTO_FATURA_PARCELADO, VALOR_PAGAMENTO_FATURA_REALIZADO) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountsBillingValueType(str, Enum):
    OUTRO_VALOR_PAGO_FATURA = "OUTRO_VALOR_PAGO_FATURA"
    VALOR_PAGAMENTO_FATURA_PARCELADO = "VALOR_PAGAMENTO_FATURA_PARCELADO"
    VALOR_PAGAMENTO_FATURA_REALIZADO = "VALOR_PAGAMENTO_FATURA_REALIZADO"

    def __str__(self) -> str:
        return str(self.value)
