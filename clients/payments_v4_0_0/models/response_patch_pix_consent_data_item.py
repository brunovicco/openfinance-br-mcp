"""Payments API model: Objeto contendo dados do pagamento."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ResponsePatchPixConsentDataItem")


@_attrs_define
class ResponsePatchPixConsentDataItem:
    """Objeto contendo dados do pagamento.

    Attributes:
        payment_id (str): Código ou identificador único informado pela instituição detentora da conta para representar
            a iniciação de pagamento individual. O `paymentId` deve ser diferente do `endToEndId`.
            Este é o identificador que deverá ser utilizado na consulta ao status da iniciação de pagamento efetuada.
             Example: TXpRMU9UQTROMWhZV2xSU1FUazJSMDl.
        status_update_date_time (datetime.datetime): Data e hora da última atualização da iniciação de pagamento.
            Uma string com data e hora conforme especificação RFC-3339,
            sempre com a utilização de timezone UTC(UTC time format).
             Example: 2020-07-21T08:30:00Z.
    """

    payment_id: str
    status_update_date_time: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payment_id = self.payment_id

        status_update_date_time = self.status_update_date_time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paymentId": payment_id,
                "statusUpdateDateTime": status_update_date_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        payment_id = d.pop("paymentId")

        status_update_date_time = isoparse(d.pop("statusUpdateDateTime"))

        response_patch_pix_consent_data_item = cls(
            payment_id=payment_id,
            status_update_date_time=status_update_date_time,
        )

        response_patch_pix_consent_data_item.additional_properties = d
        return response_patch_pix_consent_data_item

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
