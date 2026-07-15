"""Treasure Titles API model: Valor bruto da movimentação"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TreasureTitlesTransactionGrossValue")


@_attrs_define
class TreasureTitlesTransactionGrossValue:
    """Valor bruto da movimentação

    Nos casos em que se tratar de movimento de saída e a instituição não tiver a informação de IR recolhido na fonte, o
    valor bruto e o valor líquido expostos deverão ser iguais.

        Attributes:
            amount (str): Valor bruto da transação (Preço unitário da movimentação x Quantidade)  Example: 1000.04.
            currency (str): Moeda referente ao valor monetário, seguindo o modelo ISO-4217 Example: BRL.
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

        treasure_titles_transaction_gross_value = cls(
            amount=amount,
            currency=currency,
        )

        treasure_titles_transaction_gross_value.additional_properties = d
        return treasure_titles_transaction_gross_value

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
