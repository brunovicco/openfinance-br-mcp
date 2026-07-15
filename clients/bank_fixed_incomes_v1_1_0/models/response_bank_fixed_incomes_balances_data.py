"""ResponseBankFixedIncomesBalancesData: a data model of the Bank Fixed Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.bank_fixed_incomes_v1_1_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_blocked_balance import (
        ResponseBankFixedIncomesBalancesDataBlockedBalance,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_financial_transaction_tax import (
        ResponseBankFixedIncomesBalancesDataFinancialTransactionTax,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_gross_amount import (
        ResponseBankFixedIncomesBalancesDataGrossAmount,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_income_tax import (
        ResponseBankFixedIncomesBalancesDataIncomeTax,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_net_amount import (
        ResponseBankFixedIncomesBalancesDataNetAmount,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_purchase_unit_price import (
        ResponseBankFixedIncomesBalancesDataPurchaseUnitPrice,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_updated_unit_price import (
        ResponseBankFixedIncomesBalancesDataUpdatedUnitPrice,
    )


T = TypeVar("T", bound="ResponseBankFixedIncomesBalancesData")


@_attrs_define
class ResponseBankFixedIncomesBalancesData:
    """
    Attributes:
        reference_date_time (datetime.datetime): Data e hora da última posição consolidada a que se referem os dados
            transacionais do cliente disponíveis nos canais eletrônicos.
            Deve respeitar o prazo máximo de tempestividade da API, conforme a página
            ["Orientações"](https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/102957060).
            Na representação data deve se considerar os minutos e segundos como zero (00:00:00Z).

            No preenchimento do campo é esperado que a instituição informe a última vez que capturou a posição para
            compartilhamento no Open Finance. Dessa forma, é possível que:
            - Caso a instituição capture dados de forma síncrona, essa informação seja de até uma hora atrás;
            - Caso a instituição capture dados de forma assíncrona, essa informação seja de horas ou dias atrás;
            - Quando a posição for zerada: mesmo conteúdo do campo requestDateTime
             Example: 2022-07-21T17:32:00Z.
        quantity (str): Quantidade de títulos detidos na data da posição do cliente Example: 1000.0004.
        updated_unit_price (ResponseBankFixedIncomesBalancesDataUpdatedUnitPrice): Valor bruto unitário atualizado na
            data de referência.
        gross_amount (ResponseBankFixedIncomesBalancesDataGrossAmount): Valor do investimento que se refere a quantidade
            multiplicado pelo PU atualizado na data de referência;
        net_amount (ResponseBankFixedIncomesBalancesDataNetAmount): Valor do investimento atualizado na data de
            referência, posterior a dedução de impostos (IOF e IR).
        income_tax (ResponseBankFixedIncomesBalancesDataIncomeTax): Valor do imposto de renda provisionado considerando
            a alíquota vigente na data de referência.
        financial_transaction_tax (ResponseBankFixedIncomesBalancesDataFinancialTransactionTax): Valor do imposto (IOF)
            provisionado considerando a alíquota vigente na data de referência.
        blocked_balance (ResponseBankFixedIncomesBalancesDataBlockedBalance): Valor não disponível para movimentação
            naquele momento por qualquer motivo (bloqueio judicial, bloqueio em garantia, entre outros). Prazo de carência
            não é considerado como bloqueio.
        purchase_unit_price (ResponseBankFixedIncomesBalancesDataPurchaseUnitPrice): Valor unitário negociado com o
            cliente na data de aquisição
        pre_fixed_rate (str | Unset): Taxa de remuneração acordada com o cliente na contratação. Em casos de produtos
            progressivos, considerar a taxa máxima contratada.
            O preenchimento deve respeitar as 6 casas decimais, mesmo que venham preenchidas com zeros(representação de
            porcentagem p.ex: 0.150000.
            Este valor representa 15%. O valor 1 representa 100%).
            É esperado que o preenchimento deste campo pelas participantes seja enviado conforme foi acordado no momento da
            contratação.
             Example: 0.300000.
        post_fixed_indexer_percentage (str | Unset): Percentual do indexador acordado com o cliente na contratação. Em
            casos de produtos progressivos, considerar a taxa máxima contratada.
            O preenchimento deve respeitar as 6 casas decimais, mesmo que venham preenchidas com zeros(representação de
            porcentagem p.ex: 0.150000.
            Este valor representa 15%. O valor 1 representa 100%).
            É esperado que o preenchimento deste campo pelas participantes seja enviado conforme foi acordado no momento da
            contratação.
             Example: 1.000000.
    """

    reference_date_time: datetime.datetime
    quantity: str
    updated_unit_price: 'ResponseBankFixedIncomesBalancesDataUpdatedUnitPrice'
    gross_amount: 'ResponseBankFixedIncomesBalancesDataGrossAmount'
    net_amount: 'ResponseBankFixedIncomesBalancesDataNetAmount'
    income_tax: 'ResponseBankFixedIncomesBalancesDataIncomeTax'
    financial_transaction_tax: (
        'ResponseBankFixedIncomesBalancesDataFinancialTransactionTax'
    )
    blocked_balance: 'ResponseBankFixedIncomesBalancesDataBlockedBalance'
    purchase_unit_price: 'ResponseBankFixedIncomesBalancesDataPurchaseUnitPrice'
    pre_fixed_rate: str | Unset = UNSET
    post_fixed_indexer_percentage: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reference_date_time = self.reference_date_time.isoformat()

        quantity = self.quantity

        updated_unit_price = self.updated_unit_price.to_dict()

        gross_amount = self.gross_amount.to_dict()

        net_amount = self.net_amount.to_dict()

        income_tax = self.income_tax.to_dict()

        financial_transaction_tax = self.financial_transaction_tax.to_dict()

        blocked_balance = self.blocked_balance.to_dict()

        purchase_unit_price = self.purchase_unit_price.to_dict()

        pre_fixed_rate = self.pre_fixed_rate

        post_fixed_indexer_percentage = self.post_fixed_indexer_percentage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "referenceDateTime": reference_date_time,
                "quantity": quantity,
                "updatedUnitPrice": updated_unit_price,
                "grossAmount": gross_amount,
                "netAmount": net_amount,
                "incomeTax": income_tax,
                "financialTransactionTax": financial_transaction_tax,
                "blockedBalance": blocked_balance,
                "purchaseUnitPrice": purchase_unit_price,
            }
        )
        if pre_fixed_rate is not UNSET:
            field_dict["preFixedRate"] = pre_fixed_rate
        if post_fixed_indexer_percentage is not UNSET:
            field_dict["postFixedIndexerPercentage"] = post_fixed_indexer_percentage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_blocked_balance import (
            ResponseBankFixedIncomesBalancesDataBlockedBalance,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_financial_transaction_tax import (
            ResponseBankFixedIncomesBalancesDataFinancialTransactionTax,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_gross_amount import (
            ResponseBankFixedIncomesBalancesDataGrossAmount,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_income_tax import (
            ResponseBankFixedIncomesBalancesDataIncomeTax,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_net_amount import (
            ResponseBankFixedIncomesBalancesDataNetAmount,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_purchase_unit_price import (
            ResponseBankFixedIncomesBalancesDataPurchaseUnitPrice,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances_data_updated_unit_price import (
            ResponseBankFixedIncomesBalancesDataUpdatedUnitPrice,
        )

        d = dict(src_dict)
        reference_date_time = isoparse(d.pop("referenceDateTime"))

        quantity = d.pop("quantity")

        updated_unit_price = (
            ResponseBankFixedIncomesBalancesDataUpdatedUnitPrice.from_dict(
                d.pop("updatedUnitPrice")
            )
        )

        gross_amount = ResponseBankFixedIncomesBalancesDataGrossAmount.from_dict(
            d.pop("grossAmount")
        )

        net_amount = ResponseBankFixedIncomesBalancesDataNetAmount.from_dict(
            d.pop("netAmount")
        )

        income_tax = ResponseBankFixedIncomesBalancesDataIncomeTax.from_dict(
            d.pop("incomeTax")
        )

        financial_transaction_tax = (
            ResponseBankFixedIncomesBalancesDataFinancialTransactionTax.from_dict(
                d.pop("financialTransactionTax")
            )
        )

        blocked_balance = ResponseBankFixedIncomesBalancesDataBlockedBalance.from_dict(
            d.pop("blockedBalance")
        )

        purchase_unit_price = (
            ResponseBankFixedIncomesBalancesDataPurchaseUnitPrice.from_dict(
                d.pop("purchaseUnitPrice")
            )
        )

        pre_fixed_rate = d.pop("preFixedRate", UNSET)

        post_fixed_indexer_percentage = d.pop("postFixedIndexerPercentage", UNSET)

        response_bank_fixed_incomes_balances_data = cls(
            reference_date_time=reference_date_time,
            quantity=quantity,
            updated_unit_price=updated_unit_price,
            gross_amount=gross_amount,
            net_amount=net_amount,
            income_tax=income_tax,
            financial_transaction_tax=financial_transaction_tax,
            blocked_balance=blocked_balance,
            purchase_unit_price=purchase_unit_price,
            pre_fixed_rate=pre_fixed_rate,
            post_fixed_indexer_percentage=post_fixed_indexer_percentage,
        )

        response_bank_fixed_incomes_balances_data.additional_properties = d
        return response_bank_fixed_incomes_balances_data

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
