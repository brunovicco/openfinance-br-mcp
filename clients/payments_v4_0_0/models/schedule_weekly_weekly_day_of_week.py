"""ScheduleWeeklyWeeklyDayOfWeek: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class ScheduleWeeklyWeeklyDayOfWeek(str, Enum):
    DOMINGO = "DOMINGO"
    QUARTA_FEIRA = "QUARTA_FEIRA"
    QUINTA_FEIRA = "QUINTA_FEIRA"
    SABADO = "SABADO"
    SEGUNDA_FEIRA = "SEGUNDA_FEIRA"
    SEXTA_FEIRA = "SEXTA_FEIRA"
    TERCA_FEIRA = "TERCA_FEIRA"

    def __str__(self) -> str:
        return str(self.value)
