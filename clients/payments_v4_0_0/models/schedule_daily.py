"""ScheduleDaily: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.schedule_daily_daily import ScheduleDailyDaily


T = TypeVar("T", bound="ScheduleDaily")


@_attrs_define
class ScheduleDaily:
    """
    Attributes:
        daily (ScheduleDailyDaily):
    """

    daily: 'ScheduleDailyDaily'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        daily = self.daily.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "daily": daily,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.schedule_daily_daily import ScheduleDailyDaily

        d = dict(src_dict)
        daily = ScheduleDailyDaily.from_dict(d.pop("daily"))

        schedule_daily = cls(
            daily=daily,
        )

        schedule_daily.additional_properties = d
        return schedule_daily

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
