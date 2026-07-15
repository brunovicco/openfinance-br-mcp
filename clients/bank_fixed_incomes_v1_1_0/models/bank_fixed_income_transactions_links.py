"""Bank Fixed Incomes API model: Referências para outros recusos da API requisitada."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.bank_fixed_incomes_v1_1_0.types import UNSET, Unset

T = TypeVar("T", bound="BankFixedIncomeTransactionsLinks")


@_attrs_define
class BankFixedIncomeTransactionsLinks:
    """Referências para outros recusos da API requisitada.

    Attributes:
        self_ (str): URI completo que gerou a resposta atual. Example: https://api.banco.com.br/open-
            banking/api/v1/resource.
        first (str | Unset): URI da primeira página que originou essa lista de resultados. Restrição - Obrigatório
            quando não for a primeira página da resposta Example: https://api.banco.com.br/open-banking/api/v1/resource.
        prev (str | Unset): URI da página anterior dessa lista de resultados. Restrição - 	Obrigatório quando não for a
            primeira página da resposta Example: https://api.banco.com.br/open-banking/api/v1/resource.
        next_ (str | Unset): URI da próxima página dessa lista de resultados. Restrição - Obrigatório quando não for a
            última página da resposta Example: https://api.banco.com.br/open-banking/api/v1/resource.
    """

    self_: str
    first: str | Unset = UNSET
    prev: str | Unset = UNSET
    next_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        self_ = self.self_

        first = self.first

        prev = self.prev

        next_ = self.next_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "self": self_,
            }
        )
        if first is not UNSET:
            field_dict["first"] = first
        if prev is not UNSET:
            field_dict["prev"] = prev
        if next_ is not UNSET:
            field_dict["next"] = next_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        self_ = d.pop("self")

        first = d.pop("first", UNSET)

        prev = d.pop("prev", UNSET)

        next_ = d.pop("next", UNSET)

        bank_fixed_income_transactions_links = cls(
            self_=self_,
            first=first,
            prev=prev,
            next_=next_,
        )

        bank_fixed_income_transactions_links.additional_properties = d
        return bank_fixed_income_transactions_links

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
