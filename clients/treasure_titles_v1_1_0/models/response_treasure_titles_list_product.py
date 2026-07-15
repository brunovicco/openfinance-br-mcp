"""ResponseTreasureTitlesListProduct: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.treasure_titles_v1_1_0.models.response_treasure_titles_list_product_data import (
        ResponseTreasureTitlesListProductData,
    )
    from clients.treasure_titles_v1_1_0.models.treasure_titles_links import TreasureTitlesLinks
    from clients.treasure_titles_v1_1_0.models.treasure_titles_meta import TreasureTitlesMeta


T = TypeVar("T", bound="ResponseTreasureTitlesListProduct")


@_attrs_define
class ResponseTreasureTitlesListProduct:
    """
    Attributes:
        data (list[ResponseTreasureTitlesListProductData]):
        links (TreasureTitlesLinks): Referências para outros recusos da API requisitada.
        meta (TreasureTitlesMeta): Meta informações referente a API requisitada.
    """

    data: 'list[ResponseTreasureTitlesListProductData]'
    links: 'TreasureTitlesLinks'
    meta: 'TreasureTitlesMeta'

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
        from clients.treasure_titles_v1_1_0.models.response_treasure_titles_list_product_data import (
            ResponseTreasureTitlesListProductData,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_links import TreasureTitlesLinks
        from clients.treasure_titles_v1_1_0.models.treasure_titles_meta import TreasureTitlesMeta

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseTreasureTitlesListProductData.from_dict(data_item_data)

            data.append(data_item)

        links = TreasureTitlesLinks.from_dict(d.pop("links"))

        meta = TreasureTitlesMeta.from_dict(d.pop("meta"))

        response_treasure_titles_list_product = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_treasure_titles_list_product
