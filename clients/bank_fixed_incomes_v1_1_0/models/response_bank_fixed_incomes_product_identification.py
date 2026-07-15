"""ResponseBankFixedIncomesProductIdentification: a data model of the Bank Fixed Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_meta import BankFixedIncomesMeta
    from clients.bank_fixed_incomes_v1_1_0.models.identify_product import IdentifyProduct
    from clients.bank_fixed_incomes_v1_1_0.models.links import Links


T = TypeVar("T", bound="ResponseBankFixedIncomesProductIdentification")


@_attrs_define
class ResponseBankFixedIncomesProductIdentification:
    """
    Attributes:
        data (IdentifyProduct):
        links (Links): Referências para outros recusos da API requisitada.
        meta (BankFixedIncomesMeta): Meta informações referente a API requisitada.
    """

    data: 'IdentifyProduct'
    links: 'Links'
    meta: 'BankFixedIncomesMeta'

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        links = self.links.to_dict()

        meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}

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
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_meta import BankFixedIncomesMeta
        from clients.bank_fixed_incomes_v1_1_0.models.identify_product import IdentifyProduct
        from clients.bank_fixed_incomes_v1_1_0.models.links import Links

        d = dict(src_dict)
        data = IdentifyProduct.from_dict(d.pop("data"))

        links = Links.from_dict(d.pop("links"))

        meta = BankFixedIncomesMeta.from_dict(d.pop("meta"))

        response_bank_fixed_incomes_product_identification = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_bank_fixed_incomes_product_identification
