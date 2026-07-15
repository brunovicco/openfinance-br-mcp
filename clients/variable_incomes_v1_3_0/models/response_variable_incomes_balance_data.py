"""ResponseVariableIncomesBalanceData: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from clients.variable_incomes_v1_3_0.models.variable_incomes_balances_blocked_balance import (
        VariableIncomesBalancesBlockedBalance,
    )
    from clients.variable_incomes_v1_3_0.models.variable_incomes_balances_closing_price import (
        VariableIncomesBalancesClosingPrice,
    )
    from clients.variable_incomes_v1_3_0.models.variable_incomes_balances_gross_amount import (
        VariableIncomesBalancesGrossAmount,
    )


T = TypeVar("T", bound="ResponseVariableIncomesBalanceData")


@_attrs_define
class ResponseVariableIncomesBalanceData:
    """
    Attributes:
        reference_date (datetime.date): Posição fechada para o ativo da data do dia anterior. Example: 2023-01-07.
        price_factor (str): Fator que indica o número de ações utilizadas para a formação do preço. Valor informado deve
            ser maior que zero.
             Example: 100.0005.
        gross_amount (VariableIncomesBalancesGrossAmount): Valor do investimento anterior à dedução de impostos, taxas e
            tarifas (se houver), atualizado na data de referência. Quantidade de ativos dividido pelo Fator de cotação e
            multiplicado pelo pelo preço de fechamento da data de referência.
        blocked_balance (VariableIncomesBalancesBlockedBalance): Valor não disponível para movimentação naquele momento
            por qualquer motivo (bloqueio judicial, bloqueio em garantia, entre outros). Prazo de carência não é considerado
            como bloqueio.
        quantity (str): Quatidade total do ativo na data de referência. Example: 1000.00000004.
        closing_price (VariableIncomesBalancesClosingPrice): Preço de fechamento da data de referência.
    """

    reference_date: datetime.date
    price_factor: str
    gross_amount: 'VariableIncomesBalancesGrossAmount'
    blocked_balance: 'VariableIncomesBalancesBlockedBalance'
    quantity: str
    closing_price: 'VariableIncomesBalancesClosingPrice'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reference_date = self.reference_date.isoformat()

        price_factor = self.price_factor

        gross_amount = self.gross_amount.to_dict()

        blocked_balance = self.blocked_balance.to_dict()

        quantity = self.quantity

        closing_price = self.closing_price.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "referenceDate": reference_date,
                "priceFactor": price_factor,
                "grossAmount": gross_amount,
                "blockedBalance": blocked_balance,
                "quantity": quantity,
                "closingPrice": closing_price,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.variable_incomes_v1_3_0.models.variable_incomes_balances_blocked_balance import (
            VariableIncomesBalancesBlockedBalance,
        )
        from clients.variable_incomes_v1_3_0.models.variable_incomes_balances_closing_price import (
            VariableIncomesBalancesClosingPrice,
        )
        from clients.variable_incomes_v1_3_0.models.variable_incomes_balances_gross_amount import (
            VariableIncomesBalancesGrossAmount,
        )

        d = dict(src_dict)
        reference_date = isoparse(d.pop("referenceDate")).date()

        price_factor = d.pop("priceFactor")

        gross_amount = VariableIncomesBalancesGrossAmount.from_dict(
            d.pop("grossAmount")
        )

        blocked_balance = VariableIncomesBalancesBlockedBalance.from_dict(
            d.pop("blockedBalance")
        )

        quantity = d.pop("quantity")

        closing_price = VariableIncomesBalancesClosingPrice.from_dict(
            d.pop("closingPrice")
        )

        response_variable_incomes_balance_data = cls(
            reference_date=reference_date,
            price_factor=price_factor,
            gross_amount=gross_amount,
            blocked_balance=blocked_balance,
            quantity=quantity,
            closing_price=closing_price,
        )

        response_variable_incomes_balance_data.additional_properties = d
        return response_variable_incomes_balance_data

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
