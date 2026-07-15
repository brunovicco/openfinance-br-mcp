"""Variable Incomes API model: Valor líquido da nota de negociação após despesas com taxa de corretagem, taxa de liquidação, taxa de registro, taxa"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResponseVariableIncomesBrokerDataNetValue")


@_attrs_define
class ResponseVariableIncomesBrokerDataNetValue:
    """Valor líquido da nota de negociação após despesas com taxa de corretagem, taxa de liquidação, taxa de registro, taxa
    A.N.A, emolumentos, taxa de custódia, impostos e IRRF.

        Attributes:
            amount (str): Valor relacionado ao objeto. Example: 4889.0012.
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

        response_variable_incomes_broker_data_net_value = cls(
            amount=amount,
            currency=currency,
        )

        response_variable_incomes_broker_data_net_value.additional_properties = d
        return response_variable_incomes_broker_data_net_value

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
