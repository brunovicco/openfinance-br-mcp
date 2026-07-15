"""Consents API model: Meta informações referente a API requisitada."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="ConsentsDeleteConsentsConsentIdResponse529Meta")


@_attrs_define
class ConsentsDeleteConsentsConsentIdResponse529Meta:
    """Meta informações referente a API requisitada.

    Attributes:
        request_date_time (datetime.datetime): Data e hora da consulta, conforme especificação RFC-3339, formato UTC.
            Example: 2021-05-21T08:30:00Z.
    """

    request_date_time: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        request_date_time = self.request_date_time.isoformat()

        field_dict: dict[str, Any] = {}

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

        consents_delete_consents_consent_id_response_529_meta = cls(
            request_date_time=request_date_time,
        )

        return consents_delete_consents_consent_id_response_529_meta
