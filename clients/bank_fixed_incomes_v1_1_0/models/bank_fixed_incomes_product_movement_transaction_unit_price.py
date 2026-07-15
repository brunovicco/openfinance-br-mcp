"""Bank Fixed Incomes API model: Preço unitário bruto negociado na transação. Para os casos de `transactionType` definido como"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BankFixedIncomesProductMovementTransactionUnitPrice")


@_attrs_define
class BankFixedIncomesProductMovementTransactionUnitPrice:
    """Preço unitário bruto negociado na transação. Para os casos de `transactionType` definido como
    `TRANSFERENCIA_CUSTODIA`, quando o PU original (da instituição de origem) não estiver disponível para a
    transmissora, deve ser informado o PU da data de transferência. Para os demais casos vale o preço unitário original
    (da instituição de origem).

        Attributes:
            amount (str):  Example: 1000.04.
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

        bank_fixed_incomes_product_movement_transaction_unit_price = cls(
            amount=amount,
            currency=currency,
        )

        bank_fixed_incomes_product_movement_transaction_unit_price.additional_properties = d
        return bank_fixed_incomes_product_movement_transaction_unit_price

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
