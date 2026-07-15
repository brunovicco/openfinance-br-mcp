"""ResponseTreasureTitlesIdentifyProduct: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.treasure_titles_v1_1_0.models.treasure_titles_identify_product import TreasureTitlesIdentifyProduct
    from clients.treasure_titles_v1_1_0.models.treasure_titles_links import TreasureTitlesLinks
    from clients.treasure_titles_v1_1_0.models.treasure_titles_meta import TreasureTitlesMeta


T = TypeVar("T", bound="ResponseTreasureTitlesIdentifyProduct")


@_attrs_define
class ResponseTreasureTitlesIdentifyProduct:
    """
    Attributes:
        data (TreasureTitlesIdentifyProduct):
        links (TreasureTitlesLinks): Referências para outros recusos da API requisitada.
        meta (TreasureTitlesMeta): Meta informações referente a API requisitada.
    """

    data: 'TreasureTitlesIdentifyProduct'
    links: 'TreasureTitlesLinks'
    meta: 'TreasureTitlesMeta'

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
        from clients.treasure_titles_v1_1_0.models.treasure_titles_identify_product import (
            TreasureTitlesIdentifyProduct,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_links import TreasureTitlesLinks
        from clients.treasure_titles_v1_1_0.models.treasure_titles_meta import TreasureTitlesMeta

        d = dict(src_dict)
        data = TreasureTitlesIdentifyProduct.from_dict(d.pop("data"))

        links = TreasureTitlesLinks.from_dict(d.pop("links"))

        meta = TreasureTitlesMeta.from_dict(d.pop("meta"))

        response_treasure_titles_identify_product = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_treasure_titles_identify_product
