"""ResponseVariableIncomesTransactions: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.variable_incomes_v1_3_0.models.meta_single import MetaSingle
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_transactions_data import (
        ResponseVariableIncomesTransactionsData,
    )
    from clients.variable_incomes_v1_3_0.models.variable_incomes_transactions_links import (
        VariableIncomesTransactionsLinks,
    )


T = TypeVar("T", bound="ResponseVariableIncomesTransactions")


@_attrs_define
class ResponseVariableIncomesTransactions:
    """
    Attributes:
        data (list[ResponseVariableIncomesTransactionsData]):
        links (VariableIncomesTransactionsLinks): Referências para outros recusos da API requisitada.
        meta (MetaSingle): Meta informação referente a API requisitada.
    """

    data: 'list[ResponseVariableIncomesTransactionsData]'
    links: 'VariableIncomesTransactionsLinks'
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
        from clients.variable_incomes_v1_3_0.models.meta_single import MetaSingle
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_transactions_data import (
            ResponseVariableIncomesTransactionsData,
        )
        from clients.variable_incomes_v1_3_0.models.variable_incomes_transactions_links import (
            VariableIncomesTransactionsLinks,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ResponseVariableIncomesTransactionsData.from_dict(
                data_item_data
            )

            data.append(data_item)

        links = VariableIncomesTransactionsLinks.from_dict(d.pop("links"))

        meta = MetaSingle.from_dict(d.pop("meta"))

        response_variable_incomes_transactions = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_variable_incomes_transactions
