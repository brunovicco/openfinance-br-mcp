"""Credit Cards Accounts API model: Valor disponível do limite informado"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.credit_cards_v2_3_1.types import UNSET, Unset

T = TypeVar("T", bound="CreditCardsAvailableAmount")


@_attrs_define
class CreditCardsAvailableAmount:
    """Valor disponível do limite informado

    Attributes:
        amount (str | Unset): Valor disponível do limite informado expresso em valor monetário com no mínimo 2 casas e
            no máximo 4 casas decimais.

            [Restrição] O campo é obrigatório caso isLimitFlexible for igual a false.
             Example: 1000.0400.
        currency (str | Unset): Moeda referente ao limite informado, segundo modelo ISO-4217. p.ex. 'BRL.'
            Todos os saldos informados estão representados com a moeda vigente do Brasil.

            [Restrição] O campo é obrigatório caso isLimitFlexible for igual a false.
             Example: BRL.
    """

    amount: str | Unset = UNSET
    currency: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        currency = self.currency

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if amount is not UNSET:
            field_dict["amount"] = amount
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount", UNSET)

        currency = d.pop("currency", UNSET)

        credit_cards_available_amount = cls(
            amount=amount,
            currency=currency,
        )

        credit_cards_available_amount.additional_properties = d
        return credit_cards_available_amount

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
