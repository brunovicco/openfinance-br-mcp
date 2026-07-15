"""ResponseVariableIncomesProductList: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_product_list_data import (
        ResponseVariableIncomesProductListData,
    )
    from clients.variable_incomes_v1_3_0.models.variable_incomes_links import VariableIncomesLinks
    from clients.variable_incomes_v1_3_0.models.variable_incomes_meta import VariableIncomesMeta


T = TypeVar("T", bound="ResponseVariableIncomesProductList")


@_attrs_define
class ResponseVariableIncomesProductList:
    """
    Attributes:
        data (list[ResponseVariableIncomesProductListData]):
        links (VariableIncomesLinks): Referências para outros recusos da API requisitada.
        meta (VariableIncomesMeta): Meta informações referente a API requisitada.
    """

    data: 'list[ResponseVariableIncomesProductListData]'
    links: 'VariableIncomesLinks'
    meta: 'VariableIncomesMeta'

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
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_product_list_data import (
            ResponseVariableIncomesProductListData,
        )
        from clients.variable_incomes_v1_3_0.models.variable_incomes_links import VariableIncomesLinks
        from clients.variable_incomes_v1_3_0.models.variable_incomes_meta import VariableIncomesMeta

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseVariableIncomesProductListData.from_dict(data_item_data)

            data.append(data_item)

        links = VariableIncomesLinks.from_dict(d.pop("links"))

        meta = VariableIncomesMeta.from_dict(d.pop("meta"))

        response_variable_incomes_product_list = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_variable_incomes_product_list
