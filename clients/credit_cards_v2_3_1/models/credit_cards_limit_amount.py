"""Credit Cards Accounts API model: Valor total do limite concedido."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.credit_cards_v2_3_1.types import UNSET, Unset

T = TypeVar("T", bound="CreditCardsLimitAmount")


@_attrs_define
class CreditCardsLimitAmount:
    """Valor total do limite concedido.

    Attributes:
        amount (str): Valor total do limite informado expresso em valor monetário com no mínimo 2 casas e no máximo 4
            casas decimais.

            [Restrição] O campo é obrigatório caso isLimitFlexible for igual a false.
             Example: 1000.0400.
        currency (str): Moeda referente ao limite informado, segundo modelo ISO-4217. p.ex. 'BRL.'
            Todos os limite informados estão representados com a moeda vigente do Brasil.

            [Restrição] O campo é obrigatório caso isLimitFlexible for igual a false.
             Example: BRL.
        limit_amount_reason (str | Unset): Razão pela qual o valor total do limite informado está igual a zero.

            [Restrição] Campo de preenchimento obrigatório quando limitAmount for igual a 0.00.
             Example: O perfil do cliente passou por uma análise e o limite precisou ser zerado.
    """

    amount: str
    currency: str
    limit_amount_reason: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        currency = self.currency

        limit_amount_reason = self.limit_amount_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "currency": currency,
            }
        )
        if limit_amount_reason is not UNSET:
            field_dict["limitAmountReason"] = limit_amount_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount")

        currency = d.pop("currency")

        limit_amount_reason = d.pop("limitAmountReason", UNSET)

        credit_cards_limit_amount = cls(
            amount=amount,
            currency=currency,
            limit_amount_reason=limit_amount_reason,
        )

        credit_cards_limit_amount.additional_properties = d
        return credit_cards_limit_amount

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
