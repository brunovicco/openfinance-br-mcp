"""CreatePaymentConsent: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.create_payment_consent_data import CreatePaymentConsentData


T = TypeVar("T", bound="CreatePaymentConsent")


@_attrs_define
class CreatePaymentConsent:
    """
    Attributes:
        data (CreatePaymentConsentData): Objeto contendo as informações de consentimento para a iniciação de pagamento.
    """

    data: 'CreatePaymentConsentData'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.create_payment_consent_data import CreatePaymentConsentData

        d = dict(src_dict)
        data = CreatePaymentConsentData.from_dict(d.pop("data"))

        create_payment_consent = cls(
            data=data,
        )

        create_payment_consent.additional_properties = d
        return create_payment_consent

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
