"""TreasureTitlesType: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class TreasureTitlesType(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

    def __str__(self) -> str:
        return str(self.value)
