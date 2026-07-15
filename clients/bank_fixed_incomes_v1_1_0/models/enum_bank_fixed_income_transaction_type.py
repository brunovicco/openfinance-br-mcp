"""EnumBankFixedIncomeTransactionType: enum of possible values (AMORTIZACAO, APLICACAO, CANCELAMENTO, OUTROS, PAGAMENTO_JUROS, RESGATE, ...) for this field, per the Bank Fixed Incomes OpenAPI spec."""

from enum import Enum


class EnumBankFixedIncomeTransactionType(str, Enum):
    AMORTIZACAO = "AMORTIZACAO"
    APLICACAO = "APLICACAO"
    CANCELAMENTO = "CANCELAMENTO"
    OUTROS = "OUTROS"
    PAGAMENTO_JUROS = "PAGAMENTO_JUROS"
    RESGATE = "RESGATE"
    TRANSFERENCIA_CUSTODIA = "TRANSFERENCIA_CUSTODIA"
    TRANSFERENCIA_TITULARIDADE = "TRANSFERENCIA_TITULARIDADE"
    VENCIMENTO = "VENCIMENTO"

    def __str__(self) -> str:
        return str(self.value)
