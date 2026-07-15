"""EnumCreditCardAccountsFinanceChargeType: enum of possible values (IOF, JUROS_MORA_ATRASO_PAGAMENTO_FATURA, JUROS_REMUNERATORIOS_ATRASO_PAGAMENTO_FATURA, MULTA_ATRASO_PAGAMENTO_FATURA, OUTROS) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountsFinanceChargeType(str, Enum):
    IOF = "IOF"
    JUROS_MORA_ATRASO_PAGAMENTO_FATURA = "JUROS_MORA_ATRASO_PAGAMENTO_FATURA"
    JUROS_REMUNERATORIOS_ATRASO_PAGAMENTO_FATURA = (
        "JUROS_REMUNERATORIOS_ATRASO_PAGAMENTO_FATURA"
    )
    MULTA_ATRASO_PAGAMENTO_FATURA = "MULTA_ATRASO_PAGAMENTO_FATURA"
    OUTROS = "OUTROS"

    def __str__(self) -> str:
        return str(self.value)
