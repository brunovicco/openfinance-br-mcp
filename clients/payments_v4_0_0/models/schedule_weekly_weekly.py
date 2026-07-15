"""ScheduleWeeklyWeekly: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.payments_v4_0_0.models.schedule_weekly_weekly_day_of_week import ScheduleWeeklyWeeklyDayOfWeek

T = TypeVar("T", bound="ScheduleWeeklyWeekly")


@_attrs_define
class ScheduleWeeklyWeekly:
    """
    Attributes:
        day_of_week (ScheduleWeeklyWeeklyDayOfWeek): Define o dia da semana planejado para a ocorrência das liquidações.
            Example: QUINTA_FEIRA.
        start_date (datetime.date): Define o início da vigência da recorrência. Example: 2023-08-23.
        quantity (int): Define a quantidade de pagamentos que serão enviados para liquidação. Example: 10.
    """

    day_of_week: ScheduleWeeklyWeeklyDayOfWeek
    start_date: datetime.date
    quantity: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        day_of_week = self.day_of_week.value

        start_date = self.start_date.isoformat()

        quantity = self.quantity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dayOfWeek": day_of_week,
                "startDate": start_date,
                "quantity": quantity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        day_of_week = ScheduleWeeklyWeeklyDayOfWeek(d.pop("dayOfWeek"))

        start_date = isoparse(d.pop("startDate")).date()

        quantity = d.pop("quantity")

        schedule_weekly_weekly = cls(
            day_of_week=day_of_week,
            start_date=start_date,
            quantity=quantity,
        )

        schedule_weekly_weekly.additional_properties = d
        return schedule_weekly_weekly

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
