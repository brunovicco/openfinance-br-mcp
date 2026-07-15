"""TreasureTitlesCalculation: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class TreasureTitlesCalculation(str, Enum):
    DIAS_CORRIDOS = "DIAS_CORRIDOS"
    DIAS_UTEIS = "DIAS_UTEIS"

    def __str__(self) -> str:
        return str(self.value)
