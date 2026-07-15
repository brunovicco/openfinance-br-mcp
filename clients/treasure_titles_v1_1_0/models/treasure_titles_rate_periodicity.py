"""TreasureTitlesRatePeriodicity: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class TreasureTitlesRatePeriodicity(str, Enum):
    ANUAL = "ANUAL"
    DIARIO = "DIARIO"
    MENSAL = "MENSAL"
    SEMESTRAL = "SEMESTRAL"

    def __str__(self) -> str:
        return str(self.value)
