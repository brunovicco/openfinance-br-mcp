"""ResponseCreditCardAccountsIdentification: a data model of the Credit Cards Accounts API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.credit_cards_v2_3_1.models.credit_cards_accounts_identification_data import (
        CreditCardsAccountsIdentificationData,
    )
    from clients.credit_cards_v2_3_1.models.links import Links
    from clients.credit_cards_v2_3_1.models.meta import Meta


T = TypeVar("T", bound="ResponseCreditCardAccountsIdentification")


@_attrs_define
class ResponseCreditCardAccountsIdentification:
    """
    Attributes:
        data (CreditCardsAccountsIdentificationData): Conjunto de informações referentes à identificação da conta de
            pagamento pós-paga.
        links (Links): Referências para outros recusos da API requisitada.
        meta (Meta): Meta informações referente à API requisitada.
    """

    data: 'CreditCardsAccountsIdentificationData'
    links: 'Links'
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
        from clients.credit_cards_v2_3_1.models.credit_cards_accounts_identification_data import (
            CreditCardsAccountsIdentificationData,
        )
        from clients.credit_cards_v2_3_1.models.links import Links
        from clients.credit_cards_v2_3_1.models.meta import Meta

        d = dict(src_dict)
        data = CreditCardsAccountsIdentificationData.from_dict(d.pop("data"))

        links = Links.from_dict(d.pop("links"))

        meta = Meta.from_dict(d.pop("meta"))

        response_credit_card_accounts_identification = cls(
            data=data,
            links=links,
            meta=meta,
        )

        response_credit_card_accounts_identification.additional_properties = d
        return response_credit_card_accounts_identification

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
