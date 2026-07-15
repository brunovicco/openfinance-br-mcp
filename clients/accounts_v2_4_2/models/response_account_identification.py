"""ResponseAccountIdentification: a data model of the Accounts API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.accounts_v2_4_2.models.account_identification_data import AccountIdentificationData
    from clients.accounts_v2_4_2.models.links_account_id import LinksAccountId
    from clients.accounts_v2_4_2.models.meta import Meta


T = TypeVar("T", bound="ResponseAccountIdentification")


@_attrs_define
class ResponseAccountIdentification:
    """
    Attributes:
        data (AccountIdentificationData): Conjunto dos atributos que caracterizam as Contas de: depósito à vista,
            poupança e de pagamento pré-paga
        links (LinksAccountId): Referências para outros recusos da API requisitada.
        meta (Meta): Meta informações referente à API requisitada.
    """

    data: 'AccountIdentificationData'
    links: 'LinksAccountId'
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
        from clients.accounts_v2_4_2.models.account_identification_data import AccountIdentificationData
        from clients.accounts_v2_4_2.models.links_account_id import LinksAccountId
        from clients.accounts_v2_4_2.models.meta import Meta

        d = dict(src_dict)
        data = AccountIdentificationData.from_dict(d.pop("data"))

        links = LinksAccountId.from_dict(d.pop("links"))

        meta = Meta.from_dict(d.pop("meta"))

        response_account_identification = cls(
            data=data,
            links=links,
            meta=meta,
        )

        response_account_identification.additional_properties = d
        return response_account_identification

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
