"""Funds API model: Valor líquido da movimentação posterior à dedução de impostos (IOF e IR) e taxa de saída."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResponseFundsTransactionsDataTransactionNetValue")


@_attrs_define
class ResponseFundsTransactionsDataTransactionNetValue:
    """Valor líquido da movimentação posterior à dedução de impostos (IOF e IR) e taxa de saída.
    [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o valor
    'SAIDA'.

        Attributes:
            amount (str): Valor relacionado ao objeto. Example: 1000.04.
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

        response_funds_transactions_data_transaction_net_value = cls(
            amount=amount,
            currency=currency,
        )

        response_funds_transactions_data_transaction_net_value.additional_properties = d
        return response_funds_transactions_data_transaction_net_value

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
