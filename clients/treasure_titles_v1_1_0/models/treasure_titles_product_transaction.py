"""TreasureTitlesProductTransaction: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.treasure_titles_v1_1_0.models.treasure_titles_transaction_type import TreasureTitlesTransactionType
from clients.treasure_titles_v1_1_0.models.treasure_titles_type import TreasureTitlesType
from clients.treasure_titles_v1_1_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.treasure_titles_v1_1_0.models.treasure_titles_product_transaction_financial_transaction_tax import (
        TreasureTitlesProductTransactionFinancialTransactionTax,
    )
    from clients.treasure_titles_v1_1_0.models.treasure_titles_product_transaction_income_tax import (
        TreasureTitlesProductTransactionIncomeTax,
    )
    from clients.treasure_titles_v1_1_0.models.treasure_titles_transaction_gross_value import (
        TreasureTitlesTransactionGrossValue,
    )
    from clients.treasure_titles_v1_1_0.models.treasure_titles_transaction_net_value import (
        TreasureTitlesTransactionNetValue,
    )
    from clients.treasure_titles_v1_1_0.models.treasure_titles_transaction_unit_price import (
        TreasureTitlesTransactionUnitPrice,
    )


T = TypeVar("T", bound="TreasureTitlesProductTransaction")


@_attrs_define
class TreasureTitlesProductTransaction:
    """
    Attributes:
        type_ (TreasureTitlesType): Tipo de movimentação na visão de investimento (Nos casos de
            pagamento de juros e amortização) fica convencionado que será considerado que
            o tipo de movimento será saída.
             Example: ENTRADA.
        transaction_type (TreasureTitlesTransactionType): Compra, venda, cancelamento, vencimento, pagamento de juros,
            amortização, transferência de titularidade, transferência de custódia e outros. Example: AMORTIZACAO.
        transaction_date (datetime.date): Data da movimentação. Example: 2018-02-15.
        transaction_unit_price (TreasureTitlesTransactionUnitPrice): Preço unitário bruto negociado na transação.
        transaction_quantity (str): Quantidade de títulos envolvidos na movimentação. Example: 42.25.
        transaction_gross_value (TreasureTitlesTransactionGrossValue): Valor bruto da movimentação

            Nos casos em que se tratar de movimento de saída e a instituição não tiver a informação de IR recolhido na
            fonte, o valor bruto e o valor líquido expostos deverão ser iguais.
        transaction_net_value (TreasureTitlesTransactionNetValue): Valor líquido da transação

            Nos casos em que se tratar de movimento de saída e a instituição não tiver a informação de IR recolhido na
            fonte, o valor bruto e o valor líquido expostos deverão ser iguais.
        transaction_id (str): Código ou identificador único prestado pela instituição para individualizar o movimento.
            Example: ABCD2126019929279212650822221989319253344.
        transaction_type_additional_info (str | Unset): Informação adicional do tipo de movimentação, para preenchimento
            no caso de movimentações não de limitadas no domínio.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'transactionType' for
            preenchido com o valor 'OUTROS'.
        income_tax (TreasureTitlesProductTransactionIncomeTax | Unset): Valor do imposto de renda recolhido na transação

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'SAIDA'.
        financial_transaction_tax (TreasureTitlesProductTransactionFinancialTransactionTax | Unset): Valor do IOF
            recolhido na transação

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'SAIDA'.
        remuneration_transaction_rate (str | Unset): Taxa de remuneração da movimentação.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'ENTRADA'.
             Example: 0.300000.
    """

    type_: TreasureTitlesType
    transaction_type: TreasureTitlesTransactionType
    transaction_date: datetime.date
    transaction_unit_price: 'TreasureTitlesTransactionUnitPrice'
    transaction_quantity: str
    transaction_gross_value: 'TreasureTitlesTransactionGrossValue'
    transaction_net_value: 'TreasureTitlesTransactionNetValue'
    transaction_id: str
    transaction_type_additional_info: str | Unset = UNSET
    income_tax: 'TreasureTitlesProductTransactionIncomeTax | Unset' = UNSET
    financial_transaction_tax: (
        'TreasureTitlesProductTransactionFinancialTransactionTax | Unset'
    ) = UNSET
    remuneration_transaction_rate: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        transaction_type = self.transaction_type.value

        transaction_date = self.transaction_date.isoformat()

        transaction_unit_price = self.transaction_unit_price.to_dict()

        transaction_quantity = self.transaction_quantity

        transaction_gross_value = self.transaction_gross_value.to_dict()

        transaction_net_value = self.transaction_net_value.to_dict()

        transaction_id = self.transaction_id

        transaction_type_additional_info = self.transaction_type_additional_info

        income_tax: dict[str, Any] | Unset = UNSET
        if not isinstance(self.income_tax, Unset):
            income_tax = self.income_tax.to_dict()

        financial_transaction_tax: dict[str, Any] | Unset = UNSET
        if not isinstance(self.financial_transaction_tax, Unset):
            financial_transaction_tax = self.financial_transaction_tax.to_dict()

        remuneration_transaction_rate = self.remuneration_transaction_rate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "transactionType": transaction_type,
                "transactionDate": transaction_date,
                "transactionUnitPrice": transaction_unit_price,
                "transactionQuantity": transaction_quantity,
                "transactionGrossValue": transaction_gross_value,
                "transactionNetValue": transaction_net_value,
                "transactionId": transaction_id,
            }
        )
        if transaction_type_additional_info is not UNSET:
            field_dict["transactionTypeAdditionalInfo"] = (
                transaction_type_additional_info
            )
        if income_tax is not UNSET:
            field_dict["incomeTax"] = income_tax
        if financial_transaction_tax is not UNSET:
            field_dict["financialTransactionTax"] = financial_transaction_tax
        if remuneration_transaction_rate is not UNSET:
            field_dict["remunerationTransactionRate"] = remuneration_transaction_rate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.treasure_titles_v1_1_0.models.treasure_titles_product_transaction_financial_transaction_tax import (
            TreasureTitlesProductTransactionFinancialTransactionTax,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_product_transaction_income_tax import (
            TreasureTitlesProductTransactionIncomeTax,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_transaction_gross_value import (
            TreasureTitlesTransactionGrossValue,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_transaction_net_value import (
            TreasureTitlesTransactionNetValue,
        )
        from clients.treasure_titles_v1_1_0.models.treasure_titles_transaction_unit_price import (
            TreasureTitlesTransactionUnitPrice,
        )

        d = dict(src_dict)
        type_ = TreasureTitlesType(d.pop("type"))

        transaction_type = TreasureTitlesTransactionType(d.pop("transactionType"))

        transaction_date = isoparse(d.pop("transactionDate")).date()

        transaction_unit_price = TreasureTitlesTransactionUnitPrice.from_dict(
            d.pop("transactionUnitPrice")
        )

        transaction_quantity = d.pop("transactionQuantity")

        transaction_gross_value = TreasureTitlesTransactionGrossValue.from_dict(
            d.pop("transactionGrossValue")
        )

        transaction_net_value = TreasureTitlesTransactionNetValue.from_dict(
            d.pop("transactionNetValue")
        )

        transaction_id = d.pop("transactionId")

        transaction_type_additional_info = d.pop("transactionTypeAdditionalInfo", UNSET)

        _income_tax = d.pop("incomeTax", UNSET)
        income_tax: 'TreasureTitlesProductTransactionIncomeTax | Unset'
        if isinstance(_income_tax, Unset):
            income_tax = UNSET
        else:
            income_tax = TreasureTitlesProductTransactionIncomeTax.from_dict(
                _income_tax
            )

        _financial_transaction_tax = d.pop("financialTransactionTax", UNSET)
        financial_transaction_tax: (
            'TreasureTitlesProductTransactionFinancialTransactionTax | Unset'
        )
        if isinstance(_financial_transaction_tax, Unset):
            financial_transaction_tax = UNSET
        else:
            financial_transaction_tax = (
                TreasureTitlesProductTransactionFinancialTransactionTax.from_dict(
                    _financial_transaction_tax
                )
            )

        remuneration_transaction_rate = d.pop("remunerationTransactionRate", UNSET)

        treasure_titles_product_transaction = cls(
            type_=type_,
            transaction_type=transaction_type,
            transaction_date=transaction_date,
            transaction_unit_price=transaction_unit_price,
            transaction_quantity=transaction_quantity,
            transaction_gross_value=transaction_gross_value,
            transaction_net_value=transaction_net_value,
            transaction_id=transaction_id,
            transaction_type_additional_info=transaction_type_additional_info,
            income_tax=income_tax,
            financial_transaction_tax=financial_transaction_tax,
            remuneration_transaction_rate=remuneration_transaction_rate,
        )

        treasure_titles_product_transaction.additional_properties = d
        return treasure_titles_product_transaction

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
