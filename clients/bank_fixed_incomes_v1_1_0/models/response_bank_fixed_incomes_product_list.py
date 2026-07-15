"""ResponseBankFixedIncomesProductList: a data model of the Bank Fixed Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_meta import BankFixedIncomesMeta
    from clients.bank_fixed_incomes_v1_1_0.models.links import Links
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_product_list_data_item import (
        ResponseBankFixedIncomesProductListDataItem,
    )


T = TypeVar("T", bound="ResponseBankFixedIncomesProductList")


@_attrs_define
class ResponseBankFixedIncomesProductList:
    """
    Attributes:
        data (list[ResponseBankFixedIncomesProductListDataItem]):
        links (Links): Referências para outros recusos da API requisitada.
        meta (BankFixedIncomesMeta): Meta informações referente a API requisitada.
    """

    data: 'list[ResponseBankFixedIncomesProductListDataItem]'
    links: 'Links'
    meta: 'BankFixedIncomesMeta'

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

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
        from clients.bank_fixed_incomes_v1_1_0.models.links import Links
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_product_list_data_item import (
            ResponseBankFixedIncomesProductListDataItem,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseBankFixedIncomesProductListDataItem.from_dict(
                data_item_data
            )

            data.append(data_item)

        links = Links.from_dict(d.pop("links"))

        meta = BankFixedIncomesMeta.from_dict(d.pop("meta"))

        response_bank_fixed_incomes_product_list = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_bank_fixed_incomes_product_list
