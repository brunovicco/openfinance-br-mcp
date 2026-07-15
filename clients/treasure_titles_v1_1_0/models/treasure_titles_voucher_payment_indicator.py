"""TreasureTitlesVoucherPaymentIndicator: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class TreasureTitlesVoucherPaymentIndicator(str, Enum):
    NAO = "NAO"
    SIM = "SIM"

    def __str__(self) -> str:
        return str(self.value)
