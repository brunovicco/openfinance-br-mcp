"""ResponseBankFixedIncomesTransactions: a data model of the Bank Fixed Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_income_transactions_links import (
        BankFixedIncomeTransactionsLinks,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement import (
        BankFixedIncomesProductMovement,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_transactions_meta import (
        BankFixedIncomesTransactionsMeta,
    )


T = TypeVar("T", bound="ResponseBankFixedIncomesTransactions")


@_attrs_define
class ResponseBankFixedIncomesTransactions:
    """
    Attributes:
        data (list[BankFixedIncomesProductMovement]):
        links (BankFixedIncomeTransactionsLinks): Referências para outros recusos da API requisitada.
        meta (BankFixedIncomesTransactionsMeta): Meta informações referente a API requisitada.
    """

    data: 'list[BankFixedIncomesProductMovement]'
    links: 'BankFixedIncomeTransactionsLinks'
    meta: 'BankFixedIncomesTransactionsMeta'

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        links = self.links.to_dict()

        meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "data": data,
                "links": links,
                "meta": meta,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_income_transactions_links import (
            BankFixedIncomeTransactionsLinks,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement import (
            BankFixedIncomesProductMovement,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_transactions_meta import (
            BankFixedIncomesTransactionsMeta,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = BankFixedIncomesProductMovement.from_dict(data_item_data)

            data.append(data_item)

        links = BankFixedIncomeTransactionsLinks.from_dict(d.pop("links"))

        meta = BankFixedIncomesTransactionsMeta.from_dict(d.pop("meta"))

        response_bank_fixed_incomes_transactions = cls(
            data=data,
            links=links,
            meta=meta,
        )

        return response_bank_fixed_incomes_transactions
