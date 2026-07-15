"""ResponseCreatePaymentConsent: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.link_single import LinkSingle
    from clients.payments_v4_0_0.models.meta import Meta
    from clients.payments_v4_0_0.models.response_create_payment_consent_data import (
        ResponseCreatePaymentConsentData,
    )


T = TypeVar("T", bound="ResponseCreatePaymentConsent")


@_attrs_define
class ResponseCreatePaymentConsent:
    """
    Attributes:
        data (ResponseCreatePaymentConsentData): Objeto contendo as informações de consentimento para a iniciação de
            pagamento.
        links (LinkSingle): Referências para outros recusos da API requisitada.
        meta (Meta): Meta informação referente a API requisitada.
    """

    data: 'ResponseCreatePaymentConsentData'
    links: 'LinkSingle'
    meta: 'Meta'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        links = self.links.to_dict()

        meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "links": links,
                "meta": meta,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.link_single import LinkSingle
        from clients.payments_v4_0_0.models.meta import Meta
        from clients.payments_v4_0_0.models.response_create_payment_consent_data import (
            ResponseCreatePaymentConsentData,
        )

        d = dict(src_dict)
        data = ResponseCreatePaymentConsentData.from_dict(d.pop("data"))

        links = LinkSingle.from_dict(d.pop("links"))

        meta = Meta.from_dict(d.pop("meta"))

        response_create_payment_consent = cls(
            data=data,
            links=links,
            meta=meta,
        )

        response_create_payment_consent.additional_properties = d
        return response_create_payment_consent

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
