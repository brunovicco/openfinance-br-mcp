"""ResponseFundsProductIdentification: a data model of the Funds API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.funds_v1_1_0.models.funds_links import FundsLinks
    from clients.funds_v1_1_0.models.funds_meta import FundsMeta
    from clients.funds_v1_1_0.models.response_funds_product_identification_data import (
        ResponseFundsProductIdentificationData,
    )


T = TypeVar("T", bound="ResponseFundsProductIdentification")


@_attrs_define
class ResponseFundsProductIdentification:
    """
    Attributes:
        data (ResponseFundsProductIdentificationData): Informações do produto de fundo de investimento a que se refere
            investmentId.
        links (FundsLinks): Referências para outros recusos da API requisitada.
        meta (FundsMeta): Meta informações referente a API requisitada.
    """

    data: 'ResponseFundsProductIdentificationData'
    links: 'FundsLinks'
    meta: 'FundsMeta'

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
        from clients.funds_v1_1_0.models.funds_links import FundsLinks
        from clients.funds_v1_1_0.models.funds_meta import FundsMeta
        from clients.funds_v1_1_0.models.response_funds_product_identification_data import (
            ResponseFundsProductIdentificationData,
        )

        d = dict(src_dict)
        data = ResponseFundsProductIdentificationData.from_dict(d.pop("data"))

        links = FundsLinks.from_dict(d.pop("links"))

        meta = FundsMeta.from_dict(d.pop("meta"))

        response_funds_product_identification = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_funds_product_identification
