"""Accounts API model: Valor de operação contratada em caráter emergencial para cobertura de saldo devedor em conta de depósitos à vista e"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AccountOverdraftLimitsDataUnarrangedOverdraftAmount")


@_attrs_define
class AccountOverdraftLimitsDataUnarrangedOverdraftAmount:
    """Valor de operação contratada em caráter emergencial para cobertura de saldo devedor em conta de depósitos à vista e
    de excesso sobre o limite pactuado de cheque especial.

        Attributes:
            amount (str): Valor relacionado ao objeto. Example: 1000.0400.
            currency (str): Moeda referente ao valor monetário, seguindo o modelo ISO-4217. Example: BRL.
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

        account_overdraft_limits_data_unarranged_overdraft_amount = cls(
            amount=amount,
            currency=currency,
        )

        account_overdraft_limits_data_unarranged_overdraft_amount.additional_properties = d
        return account_overdraft_limits_data_unarranged_overdraft_amount

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
