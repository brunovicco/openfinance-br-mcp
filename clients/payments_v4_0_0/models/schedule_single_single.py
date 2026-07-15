"""Payments API model: Define a política de agendamento único."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ScheduleSingleSingle")


@_attrs_define
class ScheduleSingleSingle:
    """Define a política de agendamento único.

    Attributes:
        date (datetime.date): Define a data alvo da liquidação do pagamento.
            O fuso horário de Brasília deve ser utilizado para criação e racionalização sobre os dados deste campo.

            [Restrição] Esse campo deverá sempre ser no mínimo D+1 corrido, ou seja, a data imediatamente posterior em
            relação a data do consentimento considerando o fuso horário de Brasília e deverá ser no máximo D+730 corridos a
            partir da data do consentimento, também considerando o fuso horário de Brasília.
             Example: 2023-08-23.
    """

    date: datetime.date
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date = isoparse(d.pop("date")).date()

        schedule_single_single = cls(
            date=date,
        )

        schedule_single_single.additional_properties = d
        return schedule_single_single

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
