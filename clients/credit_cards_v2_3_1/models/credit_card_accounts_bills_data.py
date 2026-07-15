"""Credit Cards Accounts API model: Conjunto das informações referentes a lista de faturas associadas à conta de pagamento pós-paga"""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.credit_cards_v2_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.credit_cards_v2_3_1.models.credit_card_accounts_bill_minimum_amount import (
        CreditCardAccountsBillMinimumAmount,
    )
    from clients.credit_cards_v2_3_1.models.credit_card_accounts_bills_finance_charge import (
        CreditCardAccountsBillsFinanceCharge,
    )
    from clients.credit_cards_v2_3_1.models.credit_card_accounts_bills_payment import (
        CreditCardAccountsBillsPayment,
    )
    from clients.credit_cards_v2_3_1.models.credit_cards_bill_total_amount import CreditCardsBillTotalAmount


T = TypeVar("T", bound="CreditCardAccountsBillsData")


@_attrs_define
class CreditCardAccountsBillsData:
    """Conjunto das informações referentes a lista de faturas associadas à conta de pagamento pós-paga

    Attributes:
        bill_id (str): Informação que identifica a fatura Example: 3459087XXZTR.
        due_date (datetime.date): Data de vencimento da Fatura, que aparece para pagamento pelo cliente Example:
            2021-05-21.
        bill_total_amount (CreditCardsBillTotalAmount): Valor total da faturas.
            O campo deve assumir valor positivo para saldo devedor e negativo para saldo credor.
        bill_minimum_amount (CreditCardAccountsBillMinimumAmount): Valor do pagamento minimo da fatura
        is_instalment (bool): Indica se a fatura permite parcelamento (true) ou não (false).
        payments (list[CreditCardAccountsBillsPayment]): Lista que traz os valores relativos aos pagamentos da Fatura da
            conta de pagamento pós-paga
        finance_charges (list[CreditCardAccountsBillsFinanceCharge] | Unset): Lista dos encargos cobrados na fatura
    """

    bill_id: str
    due_date: datetime.date
    bill_total_amount: 'CreditCardsBillTotalAmount'
    bill_minimum_amount: 'CreditCardAccountsBillMinimumAmount'
    is_instalment: bool
    payments: 'list[CreditCardAccountsBillsPayment]'
    finance_charges: 'list[CreditCardAccountsBillsFinanceCharge] | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bill_id = self.bill_id

        due_date = self.due_date.isoformat()

        bill_total_amount = self.bill_total_amount.to_dict()

        bill_minimum_amount = self.bill_minimum_amount.to_dict()

        is_instalment = self.is_instalment

        payments = []
        for payments_item_data in self.payments:
            payments_item = payments_item_data.to_dict()
            payments.append(payments_item)

        finance_charges: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.finance_charges, Unset):
            finance_charges = []
            for finance_charges_item_data in self.finance_charges:
                finance_charges_item = finance_charges_item_data.to_dict()
                finance_charges.append(finance_charges_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "billId": bill_id,
                "dueDate": due_date,
                "billTotalAmount": bill_total_amount,
                "billMinimumAmount": bill_minimum_amount,
                "isInstalment": is_instalment,
                "payments": payments,
            }
        )
        if finance_charges is not UNSET:
            field_dict["financeCharges"] = finance_charges

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.credit_cards_v2_3_1.models.credit_card_accounts_bill_minimum_amount import (
            CreditCardAccountsBillMinimumAmount,
        )
        from clients.credit_cards_v2_3_1.models.credit_card_accounts_bills_finance_charge import (
            CreditCardAccountsBillsFinanceCharge,
        )
        from clients.credit_cards_v2_3_1.models.credit_card_accounts_bills_payment import (
            CreditCardAccountsBillsPayment,
        )
        from clients.credit_cards_v2_3_1.models.credit_cards_bill_total_amount import CreditCardsBillTotalAmount

        d = dict(src_dict)
        bill_id = d.pop("billId")

        due_date = isoparse(d.pop("dueDate")).date()

        bill_total_amount = CreditCardsBillTotalAmount.from_dict(
            d.pop("billTotalAmount")
        )

        bill_minimum_amount = CreditCardAccountsBillMinimumAmount.from_dict(
            d.pop("billMinimumAmount")
        )

        is_instalment = d.pop("isInstalment")

        payments = []
        _payments = d.pop("payments")
        for payments_item_data in _payments:
            payments_item = CreditCardAccountsBillsPayment.from_dict(payments_item_data)

            payments.append(payments_item)

        _finance_charges = d.pop("financeCharges", UNSET)
        finance_charges: 'list[CreditCardAccountsBillsFinanceCharge] | Unset' = UNSET
        if _finance_charges is not UNSET:
            finance_charges = []
            for finance_charges_item_data in _finance_charges:
                finance_charges_item = CreditCardAccountsBillsFinanceCharge.from_dict(
                    finance_charges_item_data
                )

                finance_charges.append(finance_charges_item)

        credit_card_accounts_bills_data = cls(
            bill_id=bill_id,
            due_date=due_date,
            bill_total_amount=bill_total_amount,
            bill_minimum_amount=bill_minimum_amount,
            is_instalment=is_instalment,
            payments=payments,
            finance_charges=finance_charges,
        )

        credit_card_accounts_bills_data.additional_properties = d
        return credit_card_accounts_bills_data

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
