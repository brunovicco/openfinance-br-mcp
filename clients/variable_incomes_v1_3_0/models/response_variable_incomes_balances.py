"""ResponseVariableIncomesBalances: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_balance_data import (
        ResponseVariableIncomesBalanceData,
    )
    from clients.variable_incomes_v1_3_0.models.variable_incomes_links import VariableIncomesLinks
    from clients.variable_incomes_v1_3_0.models.variable_incomes_meta import VariableIncomesMeta


T = TypeVar("T", bound="ResponseVariableIncomesBalances")


@_attrs_define
class ResponseVariableIncomesBalances:
    """
    Attributes:
        data (ResponseVariableIncomesBalanceData):
        links (VariableIncomesLinks): Referências para outros recusos da API requisitada.
        meta (VariableIncomesMeta): Meta informações referente a API requisitada.
    """

    data: 'ResponseVariableIncomesBalanceData'
    links: 'VariableIncomesLinks'
    meta: 'VariableIncomesMeta'

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
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_balance_data import (
            ResponseVariableIncomesBalanceData,
        )
        from clients.variable_incomes_v1_3_0.models.variable_incomes_links import VariableIncomesLinks
        from clients.variable_incomes_v1_3_0.models.variable_incomes_meta import VariableIncomesMeta

        d = dict(src_dict)
        data = ResponseVariableIncomesBalanceData.from_dict(d.pop("data"))

        links = VariableIncomesLinks.from_dict(d.pop("links"))

        meta = VariableIncomesMeta.from_dict(d.pop("meta"))

        response_variable_incomes_balances = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_variable_incomes_balances
