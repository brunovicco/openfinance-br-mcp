"""Funds API model: Informações da posição do fundo de investimento a que se refere investmentId."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from clients.funds_v1_1_0.models.funds_balances_blocked_amount import FundsBalancesBlockedAmount
    from clients.funds_v1_1_0.models.funds_balances_financial_transaction_tax_provision import (
        FundsBalancesFinancialTransactionTaxProvision,
    )
    from clients.funds_v1_1_0.models.funds_balances_gross_amount import FundsBalancesGrossAmount
    from clients.funds_v1_1_0.models.funds_balances_income_tax_provision import (
        FundsBalancesIncomeTaxProvision,
    )
    from clients.funds_v1_1_0.models.funds_balances_net_amount import FundsBalancesNetAmount
    from clients.funds_v1_1_0.models.funds_balances_quota_gross_price_value import (
        FundsBalancesQuotaGrossPriceValue,
    )


T = TypeVar("T", bound="ResponseFundsBalanceData")


@_attrs_define
class ResponseFundsBalanceData:
    """Informações da posição do fundo de investimento a que se refere investmentId.

    Attributes:
        reference_date (datetime.date): Data da última posição consolidada disponível a que se referem os dados
            transacionais do cliente disponíveis nos canais eletrônicos. Example: 2023-01-07.
        gross_amount (FundsBalancesGrossAmount): Valor do investimento que se refere a quantidade da cota x valor da
            cota, atualizado na data de referência.
        net_amount (FundsBalancesNetAmount): Valor do investimento atualizado na data de referência, posterior a dedução
            de impostos (IOF e IR) e taxa de saída, caso a instituição considere este valor na composição do saldo líquido.
            Este valor considera o valor bloqueado (blockedAmount).
        income_tax_provision (FundsBalancesIncomeTaxProvision): Valor do imposto de renda provisionado considerando a
            alíquota vigente na data de referência.
        financial_transaction_tax_provision (FundsBalancesFinancialTransactionTaxProvision): Valor do imposto
            considerando a alíquota vigente na data de referência.
        blocked_amount (FundsBalancesBlockedAmount): Valor não disponível para movimentação naquele momento por qualquer
            motivo (bloqueio judicial, bloqueio em garantia, entre outros). Prazo de carência não é considerado como
            bloqueio.
        quota_quantity (str): Quantidade de cotas detidas em posição do cliente . Example: 42.25.
        quota_gross_price_value (FundsBalancesQuotaGrossPriceValue): Valor bruto da cota atualizado na data de
            referência.
    """

    reference_date: datetime.date
    gross_amount: 'FundsBalancesGrossAmount'
    net_amount: 'FundsBalancesNetAmount'
    income_tax_provision: 'FundsBalancesIncomeTaxProvision'
    financial_transaction_tax_provision: 'FundsBalancesFinancialTransactionTaxProvision'
    blocked_amount: 'FundsBalancesBlockedAmount'
    quota_quantity: str
    quota_gross_price_value: 'FundsBalancesQuotaGrossPriceValue'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reference_date = self.reference_date.isoformat()

        gross_amount = self.gross_amount.to_dict()

        net_amount = self.net_amount.to_dict()

        income_tax_provision = self.income_tax_provision.to_dict()

        financial_transaction_tax_provision = (
            self.financial_transaction_tax_provision.to_dict()
        )

        blocked_amount = self.blocked_amount.to_dict()

        quota_quantity = self.quota_quantity

        quota_gross_price_value = self.quota_gross_price_value.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "referenceDate": reference_date,
                "grossAmount": gross_amount,
                "netAmount": net_amount,
                "incomeTaxProvision": income_tax_provision,
                "financialTransactionTaxProvision": financial_transaction_tax_provision,
                "blockedAmount": blocked_amount,
                "quotaQuantity": quota_quantity,
                "quotaGrossPriceValue": quota_gross_price_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.funds_v1_1_0.models.funds_balances_blocked_amount import FundsBalancesBlockedAmount
        from clients.funds_v1_1_0.models.funds_balances_financial_transaction_tax_provision import (
            FundsBalancesFinancialTransactionTaxProvision,
        )
        from clients.funds_v1_1_0.models.funds_balances_gross_amount import FundsBalancesGrossAmount
        from clients.funds_v1_1_0.models.funds_balances_income_tax_provision import (
            FundsBalancesIncomeTaxProvision,
        )
        from clients.funds_v1_1_0.models.funds_balances_net_amount import FundsBalancesNetAmount
        from clients.funds_v1_1_0.models.funds_balances_quota_gross_price_value import (
            FundsBalancesQuotaGrossPriceValue,
        )

        d = dict(src_dict)
        reference_date = isoparse(d.pop("referenceDate")).date()

        gross_amount = FundsBalancesGrossAmount.from_dict(d.pop("grossAmount"))

        net_amount = FundsBalancesNetAmount.from_dict(d.pop("netAmount"))

        income_tax_provision = FundsBalancesIncomeTaxProvision.from_dict(
            d.pop("incomeTaxProvision")
        )

        financial_transaction_tax_provision = (
            FundsBalancesFinancialTransactionTaxProvision.from_dict(
                d.pop("financialTransactionTaxProvision")
            )
        )

        blocked_amount = FundsBalancesBlockedAmount.from_dict(d.pop("blockedAmount"))

        quota_quantity = d.pop("quotaQuantity")

        quota_gross_price_value = FundsBalancesQuotaGrossPriceValue.from_dict(
            d.pop("quotaGrossPriceValue")
        )

        response_funds_balance_data = cls(
            reference_date=reference_date,
            gross_amount=gross_amount,
            net_amount=net_amount,
            income_tax_provision=income_tax_provision,
            financial_transaction_tax_provision=financial_transaction_tax_provision,
            blocked_amount=blocked_amount,
            quota_quantity=quota_quantity,
            quota_gross_price_value=quota_gross_price_value,
        )

        response_funds_balance_data.additional_properties = d
        return response_funds_balance_data

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
