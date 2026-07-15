"""EnumBankFixedIncomeIndexer: enum of possible values (BCP, CDI, DI, IGP_DI, IGP_M, INPC, ...) for this field, per the Bank Fixed Incomes OpenAPI spec."""

from enum import Enum


class EnumBankFixedIncomeIndexer(str, Enum):
    BCP = "BCP"
    CDI = "CDI"
    DI = "DI"
    IGP_DI = "IGP_DI"
    IGP_M = "IGP_M"
    INPC = "INPC"
    IPCA = "IPCA"
    OUTROS = "OUTROS"
    PRE_FIXADO = "PRE_FIXADO"
    SELIC = "SELIC"
    TLC = "TLC"
    TR = "TR"

    def __str__(self) -> str:
        return str(self.value)
