"""Treasure Titles API model: Meta informações referente a API requisitada."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="TreasureTitlesMeta")


@_attrs_define
class TreasureTitlesMeta:
    """Meta informações referente a API requisitada.

    Attributes:
        total_records (int): Número total de registros no resultado Example: 1.
        total_pages (int): Número total de páginas no resultado Example: 1.
        request_date_time (datetime.datetime): Data e hora da consulta, conforme especificação RFC-3339, formato UTC.
            Example: 2021-05-21T08:30:00Z.
    """

    total_records: int
    total_pages: int
    request_date_time: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        total_records = self.total_records

        total_pages = self.total_pages

        request_date_time = self.request_date_time.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "totalRecords": total_records,
                "totalPages": total_pages,
                "requestDateTime": request_date_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_records = d.pop("totalRecords")

        total_pages = d.pop("totalPages")

        request_date_time = isoparse(d.pop("requestDateTime"))

        treasure_titles_meta = cls(
            total_records=total_records,
            total_pages=total_pages,
            request_date_time=request_date_time,
        )

        return treasure_titles_meta
