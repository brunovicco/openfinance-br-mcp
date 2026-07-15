"""Credit Cards Accounts API model: Valor total do limite customizado pelo cliente nos canais eletrônicos da instituição. Esse objeto é de envio"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreditCardAccountsLimitsDataCustomizedLimitAmount")


@_attrs_define
class CreditCardAccountsLimitsDataCustomizedLimitAmount:
    """Valor total do limite customizado pelo cliente nos canais eletrônicos da instituição. Esse objeto é de envio
    obrigatório nos casos em que a instituição permita ao cliente alterar o seu limite.

        Attributes:
            amount (str): Valor total do limite informado expresso em valor monetário com no mínimo 2 casas e no máximo 4
                casas decimais.
                 Example: 1000.0400.
            currency (str): Moeda referente ao limite informado, segundo modelo ISO-4217. p.ex. 'BRL.' Todos os limite
                informados estão representados com a moeda vigente do Brasil.
                 Example: BRL.
    """

    amount: str
    currency: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        currency = self.currency

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "currency": currency,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount")

        currency = d.pop("currency")

        credit_card_accounts_limits_data_customized_limit_amount = cls(
            amount=amount,
            currency=currency,
        )

        credit_card_accounts_limits_data_customized_limit_amount.additional_properties = d
        return credit_card_accounts_limits_data_customized_limit_amount

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
