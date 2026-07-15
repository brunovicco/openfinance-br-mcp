"""ResponseFundsTransactions: a data model of the Funds API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.funds_v1_1_0.models.funds_transactions_links import FundsTransactionsLinks
    from clients.funds_v1_1_0.models.meta_single import MetaSingle
    from clients.funds_v1_1_0.models.response_funds_transactions_data import ResponseFundsTransactionsData


T = TypeVar("T", bound="ResponseFundsTransactions")


@_attrs_define
class ResponseFundsTransactions:
    """
    Attributes:
        data (list[ResponseFundsTransactionsData]):
        links (FundsTransactionsLinks): Referências para outros recusos da API requisitada.
        meta (MetaSingle): Meta informação referente a API requisitada.
    """

    data: 'list[ResponseFundsTransactionsData]'
    links: 'FundsTransactionsLinks'
    meta: 'MetaSingle'

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
        from clients.funds_v1_1_0.models.funds_transactions_links import FundsTransactionsLinks
        from clients.funds_v1_1_0.models.meta_single import MetaSingle
        from clients.funds_v1_1_0.models.response_funds_transactions_data import (
            ResponseFundsTransactionsData,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseFundsTransactionsData.from_dict(data_item_data)

            data.append(data_item)

        links = FundsTransactionsLinks.from_dict(d.pop("links"))

        meta = MetaSingle.from_dict(d.pop("meta"))

        response_funds_transactions = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_funds_transactions
