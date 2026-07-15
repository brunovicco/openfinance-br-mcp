"""ResponseCreatePixPayment: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.link_single_post import LinkSinglePost
    from clients.payments_v4_0_0.models.meta import Meta
    from clients.payments_v4_0_0.models.response_create_pix_payment_data_item import (
        ResponseCreatePixPaymentDataItem,
    )


T = TypeVar("T", bound="ResponseCreatePixPayment")


@_attrs_define
class ResponseCreatePixPayment:
    """
    Attributes:
        data (list[ResponseCreatePixPaymentDataItem]):
        links (LinkSinglePost): Referências para outros recusos da API requisitada.
        meta (Meta): Meta informação referente a API requisitada.
    """

    data: 'list[ResponseCreatePixPaymentDataItem]'
    links: 'LinkSinglePost'
    meta: 'Meta'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

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
        from clients.payments_v4_0_0.models.link_single_post import LinkSinglePost
        from clients.payments_v4_0_0.models.meta import Meta
        from clients.payments_v4_0_0.models.response_create_pix_payment_data_item import (
            ResponseCreatePixPaymentDataItem,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseCreatePixPaymentDataItem.from_dict(data_item_data)

            data.append(data_item)

        links = LinkSinglePost.from_dict(d.pop("links"))

        meta = Meta.from_dict(d.pop("meta"))

        response_create_pix_payment = cls(
            data=data,
            links=links,
            meta=meta,
        )

        response_create_pix_payment.additional_properties = d
        return response_create_pix_payment

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
