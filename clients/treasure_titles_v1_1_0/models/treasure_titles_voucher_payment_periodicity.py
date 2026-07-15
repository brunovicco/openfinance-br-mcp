"""TreasureTitlesVoucherPaymentPeriodicity: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class TreasureTitlesVoucherPaymentPeriodicity(str, Enum):
    ANUAL = "ANUAL"
    IRREGULAR = "IRREGULAR"
    MENSAL = "MENSAL"
    OUTROS = "OUTROS"
    SEMESTRAL = "SEMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"

    def __str__(self) -> str:
        return str(self.value)
