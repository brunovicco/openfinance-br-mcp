"""CreditCardAccountsBillsFinanceCharge: a data model of the Credit Cards Accounts API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_finance_charge_type import (
    EnumCreditCardAccountsFinanceChargeType,
)
from clients.credit_cards_v2_3_1.types import UNSET, Unset

T = TypeVar("T", bound="CreditCardAccountsBillsFinanceCharge")


@_attrs_define
class CreditCardAccountsBillsFinanceCharge:
    """
    Attributes:
        type_ (EnumCreditCardAccountsFinanceChargeType): Traz a denominação dos Encargos que
            incidem na fatura da conta de pagamento pós-paga. (Vide Enum)
            - Juros remuneratórios por atraso no pagamento da fatura
            - Multa por atraso no pagamento da fatura
            - Juros de mora por atraso no pagamento da fatura
            - IOF
            - Outros
        amount (str): Valor cobrado pelo encargo. Expresso em valor monetário com no mínimo 2 casas e no máximo 4 casas
            decimais. Example: 100000.0400.
        currency (str): Moeda referente ao valor cobrado pelo encargo, segundo modelo ISO-4217. p.ex. 'BRL'
            Todos os saldos informados estão representados com a moeda vigente do Brasil.
             Example: BRL.
        additional_info (str | Unset): Campo livre, de preenchimento obrigatório se selecionado tipo de encargo 'OUTROS'
            Example: Informações Adicionais.
    """

    type_: EnumCreditCardAccountsFinanceChargeType
    amount: str
    currency: str
    additional_info: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        amount = self.amount

        currency = self.currency

        additional_info = self.additional_info

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "amount": amount,
                "currency": currency,
            }
        )
        if additional_info is not UNSET:
            field_dict["additionalInfo"] = additional_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = EnumCreditCardAccountsFinanceChargeType(d.pop("type"))

        amount = d.pop("amount")

        currency = d.pop("currency")

        additional_info = d.pop("additionalInfo", UNSET)

        credit_card_accounts_bills_finance_charge = cls(
            type_=type_,
            amount=amount,
            currency=currency,
            additional_info=additional_info,
        )

        credit_card_accounts_bills_finance_charge.additional_properties = d
        return credit_card_accounts_bills_finance_charge

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
