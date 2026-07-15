"""TreasureTitlesTransactionType: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class TreasureTitlesTransactionType(str, Enum):
    AMORTIZACAO = "AMORTIZACAO"
    CANCELAMENTO = "CANCELAMENTO"
    COMPRA = "COMPRA"
    OUTROS = "OUTROS"
    PAGAMENTO_JUROS = "PAGAMENTO_JUROS"
    TRANSFERENCIA_CUSTODIA = "TRANSFERENCIA_CUSTODIA"
    TRANSFERENCIA_TITULARIDADE = "TRANSFERENCIA_TITULARIDADE"
    VENCIMENTO = "VENCIMENTO"
    VENDA = "VENDA"

    def __str__(self) -> str:
        return str(self.value)
