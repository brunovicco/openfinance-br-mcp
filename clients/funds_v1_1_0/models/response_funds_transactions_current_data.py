"""Funds API model: Informações da posição do fundo de investimento a que se refere investmentId."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from clients.funds_v1_1_0.models.enum_funds_transactions_current_transaction_type import (
    EnumFundsTransactionsCurrentTransactionType,
)
from clients.funds_v1_1_0.models.enum_funds_transactions_current_type import (
    EnumFundsTransactionsCurrentType,
)
from clients.funds_v1_1_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.funds_v1_1_0.models.response_funds_transactions_current_data_financial_transaction_tax import (
        ResponseFundsTransactionsCurrentDataFinancialTransactionTax,
    )
    from clients.funds_v1_1_0.models.response_funds_transactions_current_data_income_tax import (
        ResponseFundsTransactionsCurrentDataIncomeTax,
    )
    from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_exit_fee import (
        ResponseFundsTransactionsCurrentDataTransactionExitFee,
    )
    from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_gross_value import (
        ResponseFundsTransactionsCurrentDataTransactionGrossValue,
    )
    from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_net_value import (
        ResponseFundsTransactionsCurrentDataTransactionNetValue,
    )
    from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_quota_price import (
        ResponseFundsTransactionsCurrentDataTransactionQuotaPrice,
    )
    from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_value import (
        ResponseFundsTransactionsCurrentDataTransactionValue,
    )


T = TypeVar("T", bound="ResponseFundsTransactionsCurrentData")


@_attrs_define
class ResponseFundsTransactionsCurrentData:
    """Informações da posição do fundo de investimento a que se refere investmentId.

    Attributes:
        transaction_id (str): Código ou identificador único prestado pela instituição que mantém a representação
            individual do movimento na posição do fundo. Example: ABCD2126019929279212650822221989319253344.
        type_ (EnumFundsTransactionsCurrentType): Tipo de movimentação (Entrada ou Saída).

            ENTRADA: APLICACAO, TRANSFERENCIA_COTAS,  OUTROS.

            SAIDA: RESGATE, COME_COTAS, TRANSFERENCIA_COTAS, AMORTIZACAO, OUTROS.
             Example: ENTRADA.
        transaction_type (EnumFundsTransactionsCurrentTransactionType): O campo deve classificar a transação de
            movimentação de investimento em um dos tipos descritos (amortização, transferência de cotas, aplicação, resgate
            ou come-cotas).
            A opção OUTROS só deve ser utilizada para os casos em que de fato a transação compartilhada não possa ser
            classificada como um dos itens deste Enum, e nesse caso deve-se preencher informações adicionais.
             Example: AMORTIZACAO.
        transaction_conversion_date (datetime.date): Data da conversão da transação de movimentação do fundo de
            investimento. Example: 2023-01-07.
        transaction_quota_price (ResponseFundsTransactionsCurrentDataTransactionQuotaPrice): É o valor da cota utilizada
            na conversão para a realização da movimentação do cliente no fundo, conforme a regra prevista em regulamento -
            valor pode ser negativo.
        transaction_quota_quantity (str): Número de cotas convertidas na data da movimentação.
             Example: 42.25.
        transaction_value (ResponseFundsTransactionsCurrentDataTransactionValue): Valor solicitado pelo cliente.
        transaction_gross_value (ResponseFundsTransactionsCurrentDataTransactionGrossValue): Valor da movimentação que
            se refere a quantidade da cota x valor da cota da movimentação.
            Nos casos em que não houver movimentação de cotas, por exemplo: amortização, não considerar a regra descrita.
        transaction_type_additional_info (str | Unset): Informação adicional do tipo do motivo, para preenchimento no
            caso de movimentações não delimitadas no domínio.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'transactionType' for
            preenchido com o valor 'OUTROS'.
        income_tax (ResponseFundsTransactionsCurrentDataIncomeTax | Unset): Valor do Imposto de Renda (IR) retido na
            fonte considerando a alíquota vigente na data da movimentação.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'SAIDA'.
        financial_transaction_tax (ResponseFundsTransactionsCurrentDataFinancialTransactionTax | Unset): Valor do
            Imposto sobre Operações Financeiras (IOF) retido na fonte considerando a alíquota vigente na data da
            movimentação.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'SAIDA'.
        transaction_exit_fee (ResponseFundsTransactionsCurrentDataTransactionExitFee | Unset): Valor da taxa de saída
            considerado na movimentação.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'SAIDA'.
        transaction_net_value (ResponseFundsTransactionsCurrentDataTransactionNetValue | Unset): Valor líquido da
            movimentação posterior à dedução de impostos (IOF e IR) e taxa de saída.
            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'type' for preenchido com o
            valor 'SAIDA'.
    """

    transaction_id: str
    type_: EnumFundsTransactionsCurrentType
    transaction_type: EnumFundsTransactionsCurrentTransactionType
    transaction_conversion_date: datetime.date
    transaction_quota_price: 'ResponseFundsTransactionsCurrentDataTransactionQuotaPrice'
    transaction_quota_quantity: str
    transaction_value: 'ResponseFundsTransactionsCurrentDataTransactionValue'
    transaction_gross_value: 'ResponseFundsTransactionsCurrentDataTransactionGrossValue'
    transaction_type_additional_info: str | Unset = UNSET
    income_tax: 'ResponseFundsTransactionsCurrentDataIncomeTax | Unset' = UNSET
    financial_transaction_tax: (
        'ResponseFundsTransactionsCurrentDataFinancialTransactionTax | Unset'
    ) = UNSET
    transaction_exit_fee: (
        'ResponseFundsTransactionsCurrentDataTransactionExitFee | Unset'
    ) = UNSET
    transaction_net_value: (
        'ResponseFundsTransactionsCurrentDataTransactionNetValue | Unset'
    ) = UNSET

    def to_dict(self) -> dict[str, Any]:
        transaction_id = self.transaction_id

        type_ = self.type_.value

        transaction_type = self.transaction_type.value

        transaction_conversion_date = self.transaction_conversion_date.isoformat()

        transaction_quota_price = self.transaction_quota_price.to_dict()

        transaction_quota_quantity = self.transaction_quota_quantity

        transaction_value = self.transaction_value.to_dict()

        transaction_gross_value = self.transaction_gross_value.to_dict()

        transaction_type_additional_info = self.transaction_type_additional_info

        income_tax: dict[str, Any] | Unset = UNSET
        if not isinstance(self.income_tax, Unset):
            income_tax = self.income_tax.to_dict()

        financial_transaction_tax: dict[str, Any] | Unset = UNSET
        if not isinstance(self.financial_transaction_tax, Unset):
            financial_transaction_tax = self.financial_transaction_tax.to_dict()

        transaction_exit_fee: dict[str, Any] | Unset = UNSET
        if not isinstance(self.transaction_exit_fee, Unset):
            transaction_exit_fee = self.transaction_exit_fee.to_dict()

        transaction_net_value: dict[str, Any] | Unset = UNSET
        if not isinstance(self.transaction_net_value, Unset):
            transaction_net_value = self.transaction_net_value.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "transactionId": transaction_id,
                "type": type_,
                "transactionType": transaction_type,
                "transactionConversionDate": transaction_conversion_date,
                "transactionQuotaPrice": transaction_quota_price,
                "transactionQuotaQuantity": transaction_quota_quantity,
                "transactionValue": transaction_value,
                "transactionGrossValue": transaction_gross_value,
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
        if transaction_exit_fee is not UNSET:
            field_dict["transactionExitFee"] = transaction_exit_fee
        if transaction_net_value is not UNSET:
            field_dict["transactionNetValue"] = transaction_net_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.funds_v1_1_0.models.response_funds_transactions_current_data_financial_transaction_tax import (
            ResponseFundsTransactionsCurrentDataFinancialTransactionTax,
        )
        from clients.funds_v1_1_0.models.response_funds_transactions_current_data_income_tax import (
            ResponseFundsTransactionsCurrentDataIncomeTax,
        )
        from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_exit_fee import (
            ResponseFundsTransactionsCurrentDataTransactionExitFee,
        )
        from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_gross_value import (
            ResponseFundsTransactionsCurrentDataTransactionGrossValue,
        )
        from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_net_value import (
            ResponseFundsTransactionsCurrentDataTransactionNetValue,
        )
        from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_quota_price import (
            ResponseFundsTransactionsCurrentDataTransactionQuotaPrice,
        )
        from clients.funds_v1_1_0.models.response_funds_transactions_current_data_transaction_value import (
            ResponseFundsTransactionsCurrentDataTransactionValue,
        )

        d = dict(src_dict)
        transaction_id = d.pop("transactionId")

        type_ = EnumFundsTransactionsCurrentType(d.pop("type"))

        transaction_type = EnumFundsTransactionsCurrentTransactionType(
            d.pop("transactionType")
        )

        transaction_conversion_date = isoparse(
            d.pop("transactionConversionDate")
        ).date()

        transaction_quota_price = (
            ResponseFundsTransactionsCurrentDataTransactionQuotaPrice.from_dict(
                d.pop("transactionQuotaPrice")
            )
        )

        transaction_quota_quantity = d.pop("transactionQuotaQuantity")

        transaction_value = (
            ResponseFundsTransactionsCurrentDataTransactionValue.from_dict(
                d.pop("transactionValue")
            )
        )

        transaction_gross_value = (
            ResponseFundsTransactionsCurrentDataTransactionGrossValue.from_dict(
                d.pop("transactionGrossValue")
            )
        )

        transaction_type_additional_info = d.pop("transactionTypeAdditionalInfo", UNSET)

        _income_tax = d.pop("incomeTax", UNSET)
        income_tax: 'ResponseFundsTransactionsCurrentDataIncomeTax | Unset'
        if isinstance(_income_tax, Unset):
            income_tax = UNSET
        else:
            income_tax = ResponseFundsTransactionsCurrentDataIncomeTax.from_dict(
                _income_tax
            )

        _financial_transaction_tax = d.pop("financialTransactionTax", UNSET)
        financial_transaction_tax: (
            'ResponseFundsTransactionsCurrentDataFinancialTransactionTax | Unset'
        )
        if isinstance(_financial_transaction_tax, Unset):
            financial_transaction_tax = UNSET
        else:
            financial_transaction_tax = (
                ResponseFundsTransactionsCurrentDataFinancialTransactionTax.from_dict(
                    _financial_transaction_tax
                )
            )

        _transaction_exit_fee = d.pop("transactionExitFee", UNSET)
        transaction_exit_fee: (
            'ResponseFundsTransactionsCurrentDataTransactionExitFee | Unset'
        )
        if isinstance(_transaction_exit_fee, Unset):
            transaction_exit_fee = UNSET
        else:
            transaction_exit_fee = (
                ResponseFundsTransactionsCurrentDataTransactionExitFee.from_dict(
                    _transaction_exit_fee
                )
            )

        _transaction_net_value = d.pop("transactionNetValue", UNSET)
        transaction_net_value: (
            'ResponseFundsTransactionsCurrentDataTransactionNetValue | Unset'
        )
        if isinstance(_transaction_net_value, Unset):
            transaction_net_value = UNSET
        else:
            transaction_net_value = (
                ResponseFundsTransactionsCurrentDataTransactionNetValue.from_dict(
                    _transaction_net_value
                )
            )

        response_funds_transactions_current_data = cls(
            transaction_id=transaction_id,
            type_=type_,
            transaction_type=transaction_type,
            transaction_conversion_date=transaction_conversion_date,
            transaction_quota_price=transaction_quota_price,
            transaction_quota_quantity=transaction_quota_quantity,
            transaction_value=transaction_value,
            transaction_gross_value=transaction_gross_value,
            transaction_type_additional_info=transaction_type_additional_info,
            income_tax=income_tax,
            financial_transaction_tax=financial_transaction_tax,
            transaction_exit_fee=transaction_exit_fee,
            transaction_net_value=transaction_net_value,
        )

        return response_funds_transactions_current_data
