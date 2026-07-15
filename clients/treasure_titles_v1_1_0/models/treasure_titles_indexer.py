"""TreasureTitlesIndexer: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class TreasureTitlesIndexer(str, Enum):
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
