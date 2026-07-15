"""Accounts API model: Meta informações referente à API requisitada."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="MetaOnlyRequestDateTime")


@_attrs_define
class MetaOnlyRequestDateTime:
    """Meta informações referente à API requisitada.

    Attributes:
        request_date_time (datetime.datetime): Data e hora da consulta, conforme especificação RFC-3339, formato UTC.
            Example: 2021-05-21T08:30:00Z.
    """

    request_date_time: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        request_date_time = self.request_date_time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "requestDateTime": request_date_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        request_date_time = isoparse(d.pop("requestDateTime"))

        meta_only_request_date_time = cls(
            request_date_time=request_date_time,
        )

        meta_only_request_date_time.additional_properties = d
        return meta_only_request_date_time

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
