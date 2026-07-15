"""CreditCardAccountsBillsPayment: a data model of the Credit Cards Accounts API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_billing_value_type import (
    EnumCreditCardAccountsBillingValueType,
)
from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_payment_mode import (
    EnumCreditCardAccountsPaymentMode,
)

T = TypeVar("T", bound="CreditCardAccountsBillsPayment")


@_attrs_define
class CreditCardAccountsBillsPayment:
    """
    Attributes:
        value_type (EnumCreditCardAccountsBillingValueType): Traz os tipos dos valores relativos aos pagamentos da
            fatura da conta de pagamento pós-paga: (Vide Enum)
             - Valor de pagamento da fatura com parcelamento
             - Valor pagamento da fatura realizado
             - Outro Valor pago na fatura

             VALOR_PAGAMENTO_FATURA_PARCELADO: Quando o pagamento corresponde ao fato gerador para abertura do plano de
            parcelamento da fatura

             VALOR_PAGAMENTO_FATURA_REALIZADO: Quando o pagamento corresponde ao valor total da fatura

             OUTRO_VALOR_PAGO_FATURA: Demais casos
        payment_date (datetime.date): Data efetiva de quando o Pagamento da fatura foi realizado Example: 2021-05-21.
        payment_mode (EnumCreditCardAccountsPaymentMode): Traz as formas de efetivação do pagamento realizado: (Vide
            Enum)
            - Débito em conta corrente
            - Boleto bancário
            - Averbação em folha
            - PIX
        amount (str): Valor pagamento segundo o valueType.
            Expresso em valor monetário com no mínimo 2 casas e no máximo 4 casas decimais.
            O campo não pode assumir valor negativo por se tratar de um pagamento.
             Example: 1000.0400.
        currency (str): Moeda referente ao valor de pagamento da fatura, segundo modelo ISO-4217. p.ex. 'BRL' Todos os
            valores informados estão representados com a moeda vigente do Brasil
             Example: BRL.
    """

    value_type: EnumCreditCardAccountsBillingValueType
    payment_date: datetime.date
    payment_mode: EnumCreditCardAccountsPaymentMode
    amount: str
    currency: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value_type = self.value_type.value

        payment_date = self.payment_date.isoformat()

        payment_mode = self.payment_mode.value

        amount = self.amount

        currency = self.currency

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "valueType": value_type,
                "paymentDate": payment_date,
                "paymentMode": payment_mode,
                "amount": amount,
                "currency": currency,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value_type = EnumCreditCardAccountsBillingValueType(d.pop("valueType"))

        payment_date = isoparse(d.pop("paymentDate")).date()

        payment_mode = EnumCreditCardAccountsPaymentMode(d.pop("paymentMode"))

        amount = d.pop("amount")

        currency = d.pop("currency")

        credit_card_accounts_bills_payment = cls(
            value_type=value_type,
            payment_date=payment_date,
            payment_mode=payment_mode,
            amount=amount,
            currency=currency,
        )

        credit_card_accounts_bills_payment.additional_properties = d
        return credit_card_accounts_bills_payment

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
