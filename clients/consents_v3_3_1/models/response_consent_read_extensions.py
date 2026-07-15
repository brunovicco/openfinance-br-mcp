"""ResponseConsentReadExtensions: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.consents_v3_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.links import Links
    from clients.consents_v3_3_1.models.meta_extensions import MetaExtensions
    from clients.consents_v3_3_1.models.response_consent_read_extensions_data_item import (
        ResponseConsentReadExtensionsDataItem,
    )


T = TypeVar("T", bound="ResponseConsentReadExtensions")


@_attrs_define
class ResponseConsentReadExtensions:
    """
    Attributes:
        data (list[ResponseConsentReadExtensionsDataItem]):
        links (Links | Unset): Referências para outros recusos da API requisitada.
        meta (MetaExtensions | Unset): Meta informações referente à API requisitada.
    """

    data: 'list[ResponseConsentReadExtensionsDataItem]'
    links: 'Links | Unset' = UNSET
    meta: 'MetaExtensions | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        links: dict[str, Any] | Unset = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()

        meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )
        if links is not UNSET:
            field_dict["links"] = links
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.links import Links
        from clients.consents_v3_3_1.models.meta_extensions import MetaExtensions
        from clients.consents_v3_3_1.models.response_consent_read_extensions_data_item import (
            ResponseConsentReadExtensionsDataItem,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseConsentReadExtensionsDataItem.from_dict(data_item_data)

            data.append(data_item)

        _links = d.pop("links", UNSET)
        links: 'Links | Unset'
        if isinstance(_links, Unset):
            links = UNSET
        else:
            links = Links.from_dict(_links)

        _meta = d.pop("meta", UNSET)
        meta: 'MetaExtensions | Unset'
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = MetaExtensions.from_dict(_meta)

        response_consent_read_extensions = cls(
            data=data,
            links=links,
            meta=meta,
        )

        response_consent_read_extensions.additional_properties = d
        return response_consent_read_extensions

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
