"""TreasureTitlesBalances: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.treasure_titles_v1_1_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.treasure_titles_v1_1_0.models.treasure_titles_blocked_balance import TreasureTitlesBlockedBalance
    from clients.treasure_titles_v1_1_0.models.treasure_titles_financial_transaction_tax import (
        TreasureTitlesFinancialTransactionTax,
    )
    from clients.treasure_titles_v1_1_0.models.treasure_titles_gross_amount import TreasureTitlesGrossAmount
    from clients.treasure_titles_v1_1_0.models.treasure_titles_income_tax import TreasureTitlesIncomeTax
    from clients.treasure_titles_v1_1_0.models.treasure_titles_net_amount import TreasureTitlesNetAmount
    from clients.treasure_titles_v1_1_0.models.treasure_titles_purchase_unit_price import (
        TreasureTitlesPurchaseUnitPrice,
    )
    from clients.treasure_titles_v1_1_0.models.treasure_titles_updated_unit_price import (
        TreasureTitlesUpdatedUnitPrice,
    )


T = TypeVar("T", bound="TreasureTitlesBalances")


@_attrs_define
class TreasureTitlesBalances:
    """
    Attributes:
        reference_date_time (datetime.datetime): Data da última posição consolidada disponível a que se referem os dados
            transacionais do cliente disponíveis nos canais eletrônicos. Example: 2022-07-21T17:32:00Z.
        updated_unit_price (TreasureTitlesUpdatedUnitPrice): Valor bruto unitário atualizado (a mercado) na data de
            referência.
        gross_amount (TreasureTitlesGrossAmount): Valor do investimento anterior à dedução de impostos, taxas e tarifas
            (se houver), atualizado (a mercado) na data de referência. Importante: Apenas o imposto e o IOF são
            compartilhados na versão atual da especificação, porém outras taxas podem ser aplicáveis no cálculo desse valor.
        net_amount (TreasureTitlesNetAmount): Valor do investimento posterior a dedução de impostos, taxas e tarifas (se
            houver), atualizado (a mercado) na data de referência. Importante: Apenas o imposto e o IOF são compartilhados
            na versão atual da especificação, porém outras taxas podem ser aplicáveis no cálculo desse valor.
        income_tax (TreasureTitlesIncomeTax): Valor do imposto de renda provisionado considerando a alíquota vigente na
            data de referência.
        blocked_balance (TreasureTitlesBlockedBalance): Valor não disponível para movimentação naquele momento por
            qualquer motivo (bloqueio judicial, bloqueio em garantia, entre outros). Prazo de carência não é considerado
            como bloqueio.
        purchase_unit_price (TreasureTitlesPurchaseUnitPrice): Valor unitário negociado com o cliente na data de
            aquisição.
        quantity (str): Quantidade de títulos detidos na data da posição do cliente. Example: 1000.015.
        financial_transaction_tax (TreasureTitlesFinancialTransactionTax | Unset): IOF provisionado.

            Caso seja um produto com alíquota zero esse objeto pode ser enviado sem valores (vazio).
    """

    reference_date_time: datetime.datetime
    updated_unit_price: 'TreasureTitlesUpdatedUnitPrice'
    gross_amount: 'TreasureTitlesGrossAmount'
    net_amount: 'TreasureTitlesNetAmount'
    income_tax: 'TreasureTitlesIncomeTax'
    blocked_balance: 'TreasureTitlesBlockedBalance'
    purchase_unit_price: 'TreasureTitlesPurchaseUnitPrice'
    quantity: str
    financial_transaction_tax: 'TreasureTitlesFinancialTransactionTax | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reference_date_time = self.reference_date_time.isoformat()

        updated_unit_price = self.updated_unit_price.to_dict()

        gross_amount = self.gross_amount.to_dict()

        net_amount = self.net_amount.to_dict()

        income_tax = self.income_tax.to_dict()

        blocked_balance = self.blocked_balance.to_dict()

        purchase_unit_price = self.purchase_unit_price.to_dict()

        quantity = self.quantity

        financial_transaction_tax: dict[str, Any] | Unset = UNSET
        if not isinstance(self.financial_transaction_tax, Unset):
            financial_transaction_tax = self.financial_transaction_tax.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "referenceDateTime": reference_date_time,
                "updatedUnitPrice": updated_unit_price,
                "grossAmount": gross_amount,
                "netAmount": net_amount,
                "incomeTax": income_tax,
                "blockedBalance": blocked_balance,
                "purchaseUnitPrice": purchase_unit_price,
                "quantity": quantity,
            }
        )
        if financial_transaction_tax is not UNSET:
            field_dict["financialTransactionTax"] = financial_transaction_tax

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.treasure_titles_v1_1_0.models.treasure_titles_blocked_balance import (
            TreasureTitlesBlockedBalance,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_financial_transaction_tax import (
            TreasureTitlesFinancialTransactionTax,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_gross_amount import TreasureTitlesGrossAmount
        from clients.treasure_titles_v1_1_0.models.treasure_titles_income_tax import TreasureTitlesIncomeTax
        from clients.treasure_titles_v1_1_0.models.treasure_titles_net_amount import TreasureTitlesNetAmount
        from clients.treasure_titles_v1_1_0.models.treasure_titles_purchase_unit_price import (
            TreasureTitlesPurchaseUnitPrice,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_updated_unit_price import (
            TreasureTitlesUpdatedUnitPrice,
        )

        d = dict(src_dict)
        reference_date_time = isoparse(d.pop("referenceDateTime"))

        updated_unit_price = TreasureTitlesUpdatedUnitPrice.from_dict(
            d.pop("updatedUnitPrice")
        )

        gross_amount = TreasureTitlesGrossAmount.from_dict(d.pop("grossAmount"))

        net_amount = TreasureTitlesNetAmount.from_dict(d.pop("netAmount"))

        income_tax = TreasureTitlesIncomeTax.from_dict(d.pop("incomeTax"))

        blocked_balance = TreasureTitlesBlockedBalance.from_dict(
            d.pop("blockedBalance")
        )

        purchase_unit_price = TreasureTitlesPurchaseUnitPrice.from_dict(
            d.pop("purchaseUnitPrice")
        )

        quantity = d.pop("quantity")

        _financial_transaction_tax = d.pop("financialTransactionTax", UNSET)
        financial_transaction_tax: 'TreasureTitlesFinancialTransactionTax | Unset'
        if isinstance(_financial_transaction_tax, Unset):
            financial_transaction_tax = UNSET
        else:
            financial_transaction_tax = TreasureTitlesFinancialTransactionTax.from_dict(
                _financial_transaction_tax
            )

        treasure_titles_balances = cls(
            reference_date_time=reference_date_time,
            updated_unit_price=updated_unit_price,
            gross_amount=gross_amount,
            net_amount=net_amount,
            income_tax=income_tax,
            blocked_balance=blocked_balance,
            purchase_unit_price=purchase_unit_price,
            quantity=quantity,
            financial_transaction_tax=financial_transaction_tax,
        )

        treasure_titles_balances.additional_properties = d
        return treasure_titles_balances

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
