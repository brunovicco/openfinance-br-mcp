"""Payments API model: [Restrição] As datas enviadas na lista de datas (array “dates”) não podem ser repetidas."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ScheduleCustomCustom")


@_attrs_define
class ScheduleCustomCustom:
    """[Restrição] As datas enviadas na lista de datas (array “dates”) não podem ser repetidas.
    Caso datas repetidas sejam enviadas, o detentor deve rejeitar a criação do consentimento, informando o erro
    PARAMETRO_INVALIDO.

        Attributes:
            dates (list[datetime.date]): Define os dias em que estão planejadas as ocorrências das liquidações. Example:
                ['2023-08-23', '2023-09-26'].
            additional_information (str): Texto livre para Iniciador preencher de forma compreensível pelo usuário
                aprovador/pagador.
                O texto pode ser utilizado pelo detentor para exibição do resumo da transação durante aprovação do usuário
                aprovador/pagador.
                 Example: Todas quintas e domingos por 6 meses.
    """

    dates: list[datetime.date]
    additional_information: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dates = []
        for dates_item_data in self.dates:
            dates_item = dates_item_data.isoformat()
            dates.append(dates_item)

        additional_information = self.additional_information

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dates": dates,
                "additionalInformation": additional_information,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dates = []
        _dates = d.pop("dates")
        for dates_item_data in _dates:
            dates_item = isoparse(dates_item_data).date()

            dates.append(dates_item)

        additional_information = d.pop("additionalInformation")

        schedule_custom_custom = cls(
            dates=dates,
            additional_information=additional_information,
        )

        schedule_custom_custom.additional_properties = d
        return schedule_custom_custom

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
