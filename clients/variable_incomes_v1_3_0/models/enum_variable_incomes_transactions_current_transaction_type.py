"""EnumVariableIncomesTransactionsCurrentTransactionType: enum of possible values (ALUGUEIS, COMPRA, DIVIDENDOS, JCP, OUTROS, TRANSFERENCIA_CUSTODIA, ...) for this field, per the Variable Incomes OpenAPI spec."""

from enum import Enum


class EnumVariableIncomesTransactionsCurrentTransactionType(str, Enum):
    ALUGUEIS = "ALUGUEIS"
    COMPRA = "COMPRA"
    DIVIDENDOS = "DIVIDENDOS"
    JCP = "JCP"
    OUTROS = "OUTROS"
    TRANSFERENCIA_CUSTODIA = "TRANSFERENCIA_CUSTODIA"
    TRANSFERENCIA_TITULARIDADE = "TRANSFERENCIA_TITULARIDADE"
    VENDA = "VENDA"

    def __str__(self) -> str:
        return str(self.value)
