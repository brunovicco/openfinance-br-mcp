"""ResponseFundsProductList: a data model of the Funds API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.funds_v1_1_0.models.funds_links import FundsLinks
    from clients.funds_v1_1_0.models.funds_meta import FundsMeta
    from clients.funds_v1_1_0.models.response_funds_product_list_data import ResponseFundsProductListData


T = TypeVar("T", bound="ResponseFundsProductList")


@_attrs_define
class ResponseFundsProductList:
    """
    Attributes:
        data (list[ResponseFundsProductListData]):
        links (FundsLinks): Referências para outros recusos da API requisitada.
        meta (FundsMeta): Meta informações referente a API requisitada.
    """

    data: 'list[ResponseFundsProductListData]'
    links: 'FundsLinks'
    meta: 'FundsMeta'

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
        from clients.funds_v1_1_0.models.funds_links import FundsLinks
        from clients.funds_v1_1_0.models.funds_meta import FundsMeta
        from clients.funds_v1_1_0.models.response_funds_product_list_data import (
            ResponseFundsProductListData,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseFundsProductListData.from_dict(data_item_data)

            data.append(data_item)

        links = FundsLinks.from_dict(d.pop("links"))

        meta = FundsMeta.from_dict(d.pop("meta"))

        response_funds_product_list = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_funds_product_list
