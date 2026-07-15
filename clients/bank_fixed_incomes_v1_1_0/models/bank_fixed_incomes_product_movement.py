"""BankFixedIncomesProductMovement: a data model of the Bank Fixed Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from clients.bank_fixed_incomes_v1_1_0.models.enum_bank_fixed_income_movement_type import (
    EnumBankFixedIncomeMovementType,
)
from clients.bank_fixed_incomes_v1_1_0.models.enum_bank_fixed_income_transaction_type import (
    EnumBankFixedIncomeTransactionType,
)
from clients.bank_fixed_incomes_v1_1_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_financial_transaction_tax import (
        BankFixedIncomesProductMovementFinancialTransactionTax,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_income_tax import (
        BankFixedIncomesProductMovementIncomeTax,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_transaction_gross_value import (
        BankFixedIncomesProductMovementTransactionGrossValue,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_transaction_net_value import (
        BankFixedIncomesProductMovementTransactionNetValue,
    )
    from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_transaction_unit_price import (
        BankFixedIncomesProductMovementTransactionUnitPrice,
    )


T = TypeVar("T", bound="BankFixedIncomesProductMovement")


@_attrs_define
class BankFixedIncomesProductMovement:
    """
    Attributes:
        type_ (EnumBankFixedIncomeMovementType): Tipo de movimentação na visão de investimento

            - ENTRADA: APLICACAO, CANCELAMENTO, TRANSFERENCIA_TITULARIDADE, TRANSFERENCIA_CUSTODIA, OUTROS.

            - SAIDA: RESGATE, CANCELAMENTO, VENCIMENTO, PAGAMENTO_JUROS, AMORTIZACAO, TRANSFERENCIA_TITULARIDADE,
            TRANSFERENCIA_CUSTODIA, OUTROS.

            Por exemplo, para movimentação de CANCELAMENTO, tipicamente, será o type contrário ao evento originário. Ou
            seja, para cancelamento de APLICACAO, considera-se type SAIDA; para cancelamento de RESGATE, considera-se type
            ENTRADA.
             Example: ENTRADA.
        transaction_type (EnumBankFixedIncomeTransactionType): Aplicação, resgate, cancelamento, vencimento, pagamento
            de juros, amortização, transferência de titularidade, transferência de custódia e outros. Para movimentos de
            transferência (titularidade ou custódia) deve ser considerado o preço unitário (transactionUnitPrice) da
            aquisição do título. Example: APLICACAO.
        transaction_date (datetime.date): Data da movimentação. Example: 2018-02-15.
        transaction_unit_price (BankFixedIncomesProductMovementTransactionUnitPrice): Preço unitário bruto negociado
            na transação. Para os casos de `transactionType` definido como `TRANSFERENCIA_CUSTODIA`, quando o PU original
            (da instituição de origem) não estiver disponível para a transmissora, deve ser informado o PU da data de
            transferência. Para os demais casos vale o preço unitário original (da instituição de origem).
        transaction_quantity (str): Quantidade de títulos envolvidos na movimentação. Example: 42.25.
        transaction_gross_value (BankFixedIncomesProductMovementTransactionGrossValue): Valor bruto da transação (Preço
            unitário da movimentação x Quantidade).
        transaction_net_value (BankFixedIncomesProductMovementTransactionNetValue): Valor líquido da transação.
        transaction_id (str): Código ou identificador único prestado pela instituição que mantém a representação
            individual do movimento. Example: ABCD2126019929279212650822221989319253344.
        transaction_type_additional_info (str | Unset): Informação adicional do tipo de movimentação, para preenchimento
            no caso de movimentações não delimitadas no domínio.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando houver 'Outros' no campo Motivo da
            movimentação.
        income_tax (BankFixedIncomesProductMovementIncomeTax | Unset): Valor do imposto de renda recolhido na transação.

            [Restrição] Campo de preenchimento obrigatório para os produtos aos quais essa taxa se aplica quando o campo
            `type` for preenchido com o valor `SAIDA`.
        financial_transaction_tax (BankFixedIncomesProductMovementFinancialTransactionTax | Unset): Valor do IOF
            recolhido na transação.

            [Restrição] Campo de preenchimento obrigatório para os produtos aos quais essa taxa se aplica quando o campo
            `type` for preenchido com o valor `SAIDA`.
        remuneration_transaction_rate (str | Unset): Taxa de remuneração da transação.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'ENTRADA' e se tratar de produto prefixado ou híbrido.
             Example: 0.300000.
        indexer_percentage (str | Unset): Percentual máximo do indexador acordado com o cliente na contratação.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'ENTRADA' e se tratar de produto pós-fixado ou híbrido.
             Example: 1.100000.
    """

    type_: EnumBankFixedIncomeMovementType
    transaction_type: EnumBankFixedIncomeTransactionType
    transaction_date: datetime.date
    transaction_unit_price: 'BankFixedIncomesProductMovementTransactionUnitPrice'
    transaction_quantity: str
    transaction_gross_value: 'BankFixedIncomesProductMovementTransactionGrossValue'
    transaction_net_value: 'BankFixedIncomesProductMovementTransactionNetValue'
    transaction_id: str
    transaction_type_additional_info: str | Unset = UNSET
    income_tax: 'BankFixedIncomesProductMovementIncomeTax | Unset' = UNSET
    financial_transaction_tax: (
        'BankFixedIncomesProductMovementFinancialTransactionTax | Unset'
    ) = UNSET
    remuneration_transaction_rate: str | Unset = UNSET
    indexer_percentage: str | Unset = UNSET

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

        indexer_percentage = self.indexer_percentage

        field_dict: dict[str, Any] = {}

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
        if indexer_percentage is not UNSET:
            field_dict["indexerPercentage"] = indexer_percentage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_financial_transaction_tax import (
            BankFixedIncomesProductMovementFinancialTransactionTax,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_income_tax import (
            BankFixedIncomesProductMovementIncomeTax,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_transaction_gross_value import (
            BankFixedIncomesProductMovementTransactionGrossValue,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_transaction_net_value import (
            BankFixedIncomesProductMovementTransactionNetValue,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.bank_fixed_incomes_product_movement_transaction_unit_price import (
            BankFixedIncomesProductMovementTransactionUnitPrice,
        )

        d = dict(src_dict)
        type_ = EnumBankFixedIncomeMovementType(d.pop("type"))

        transaction_type = EnumBankFixedIncomeTransactionType(d.pop("transactionType"))

        transaction_date = isoparse(d.pop("transactionDate")).date()

        transaction_unit_price = (
            BankFixedIncomesProductMovementTransactionUnitPrice.from_dict(
                d.pop("transactionUnitPrice")
            )
        )

        transaction_quantity = d.pop("transactionQuantity")

        transaction_gross_value = (
            BankFixedIncomesProductMovementTransactionGrossValue.from_dict(
                d.pop("transactionGrossValue")
            )
        )

        transaction_net_value = (
            BankFixedIncomesProductMovementTransactionNetValue.from_dict(
                d.pop("transactionNetValue")
            )
        )

        transaction_id = d.pop("transactionId")

        transaction_type_additional_info = d.pop("transactionTypeAdditionalInfo", UNSET)

        _income_tax = d.pop("incomeTax", UNSET)
        income_tax: 'BankFixedIncomesProductMovementIncomeTax | Unset'
        if isinstance(_income_tax, Unset):
            income_tax = UNSET
        else:
            income_tax = BankFixedIncomesProductMovementIncomeTax.from_dict(_income_tax)

        _financial_transaction_tax = d.pop("financialTransactionTax", UNSET)
        financial_transaction_tax: (
            'BankFixedIncomesProductMovementFinancialTransactionTax | Unset'
        )
        if isinstance(_financial_transaction_tax, Unset):
            financial_transaction_tax = UNSET
        else:
            financial_transaction_tax = (
                BankFixedIncomesProductMovementFinancialTransactionTax.from_dict(
                    _financial_transaction_tax
                )
            )

        remuneration_transaction_rate = d.pop("remunerationTransactionRate", UNSET)

        indexer_percentage = d.pop("indexerPercentage", UNSET)

        bank_fixed_incomes_product_movement = cls(
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
            indexer_percentage=indexer_percentage,
        )

        return bank_fixed_incomes_product_movement
