"""ResponseVariableIncomesTransactionsCurrentData: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from clients.variable_incomes_v1_3_0.models.enum_variable_incomes_transactions_current_transaction_type import (
    EnumVariableIncomesTransactionsCurrentTransactionType,
)
from clients.variable_incomes_v1_3_0.models.enum_variable_incomes_transactions_current_type import (
    EnumVariableIncomesTransactionsCurrentType,
)
from clients.variable_incomes_v1_3_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_transactions_current_data_transaction_unit_price import (
        ResponseVariableIncomesTransactionsCurrentDataTransactionUnitPrice,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_transactions_current_data_transaction_value import (
        ResponseVariableIncomesTransactionsCurrentDataTransactionValue,
    )


T = TypeVar("T", bound="ResponseVariableIncomesTransactionsCurrentData")


@_attrs_define
class ResponseVariableIncomesTransactionsCurrentData:
    """
    Attributes:
        type_ (EnumVariableIncomesTransactionsCurrentType): Tipo de movimentação na visão de investimento: entrada ou
            saída. Nos casos de pagamento de dividendos, JCP e aluguéis, fica convencionado que será considerado que o tipo
            de movimento será saída.
             Example: SAIDA.
        transaction_type (EnumVariableIncomesTransactionsCurrentTransactionType): O campo deve classificar a
            movimentação em um dos tipos descritos: compra, venda, dividendos, JCP, aluguéis, transferência de custódia,
            transferência de titularidade e outros.
            O transmissor deve classificar as movimentações disponíveis associando-a a um dos itens do Enum listado neste
            campo.
            A opção OUTROS só deve ser utilizada para os casos em que de fato a movimentação compartilhada não possa ser
            classificada como um dos itens deste Enum.
            A expressão “aluguéis” deverá ser utilizada apenas para informar os juros/remuneração pagos/recebidos pelo
            cliente dos contratos de ações alugadas, seguindo o mesmo entendimento de ENTRADA/SAÍDA da expressão
            “dividendos”.
             Example: DIVIDENDOS.
        transaction_date (datetime.date): Data da movimentação de acordo com a data visualizada pelo cliente nos canais
            da instituição. Data do pregão: compartilhar movimentos até a data da posição.
             Example: 2018-02-15.
        transaction_value (ResponseVariableIncomesTransactionsCurrentDataTransactionValue): Valor da operação realizada
            pelo cliente.
        transaction_id (str): Código ou identificador único prestado pela instituição que mantém a representação
            individual do movimento. Example: ABCD2126019929279212650822221989319253344.
        transaction_type_additional_info (str | Unset): Informação adicional do tipo de movimentação, para preenchimento
            no caso de movimentações não delimitadas no domínio.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'transactionType' for
            preenchido com o valor 'OUTROS'.
        price_factor (str | Unset): Fator que indica o número de ações utilizadas para a formação do preço. Valor
            informado deve ser maior que zero.
             Example: 100.0005.
        transaction_unit_price (ResponseVariableIncomesTransactionsCurrentDataTransactionUnitPrice | Unset): Preço
            unitário da movimentação: valor da unidade do produto na movimentação do investimento. Em transferências de
            custódia, quando o PU original (da instituição de origem) não estiver disponível para a transmissora, deve ser
            informado o PU marcado pela instituição na data de transferência.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo `transactionType` for
            preenchido com os valores `COMPRA` ou `VENDA`.
        transaction_quantity (str | Unset): Quantidade de ativos movimentados.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'transactionType' for
            preenchido com os valores 'COMPRA' ou 'VENDA'.
             Example: 42.00000025.
        broker_note_id (str | Unset): Identifica de forma única o relacionamento do cliente com o produto para cada
            número de nota de negociação (`brokerNoteNumber`), mantendo as regras de imutabilidade dentro da instituição
            transmissora.
            O conteúdo desse campo deve ser utilizado como parâmetro na chamada do endpoint `GET /broker-
            notes/{brokerNoteId}`.

            A relação entre `investmentId` e `brokerNoteId` é de N para N, refletindo que uma nota de negociação pode
            contemplar múltiplos investimentos e, ao mesmo tempo, um investimento pode estar associado a diferentes notas de
            negociação.

            A relação entre `brokerNoteId` e `brokerNoteNumber` é de 1 para 1, garantindo que cada nota de negociação
            natural corresponda a um identificador único e imutável no ecossistema.

            [Restrição] Informação de envio obrigatório caso o motivo da movimentação seja compra ou venda.
             Example: XWYZ555019929279212650822221989319252233.
    """

    type_: EnumVariableIncomesTransactionsCurrentType
    transaction_type: EnumVariableIncomesTransactionsCurrentTransactionType
    transaction_date: datetime.date
    transaction_value: 'ResponseVariableIncomesTransactionsCurrentDataTransactionValue'
    transaction_id: str
    transaction_type_additional_info: str | Unset = UNSET
    price_factor: str | Unset = UNSET
    transaction_unit_price: (
        'ResponseVariableIncomesTransactionsCurrentDataTransactionUnitPrice | Unset'
    ) = UNSET
    transaction_quantity: str | Unset = UNSET
    broker_note_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        transaction_type = self.transaction_type.value

        transaction_date = self.transaction_date.isoformat()

        transaction_value = self.transaction_value.to_dict()

        transaction_id = self.transaction_id

        transaction_type_additional_info = self.transaction_type_additional_info

        price_factor = self.price_factor

        transaction_unit_price: dict[str, Any] | Unset = UNSET
        if not isinstance(self.transaction_unit_price, Unset):
            transaction_unit_price = self.transaction_unit_price.to_dict()

        transaction_quantity = self.transaction_quantity

        broker_note_id = self.broker_note_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "transactionType": transaction_type,
                "transactionDate": transaction_date,
                "transactionValue": transaction_value,
                "transactionId": transaction_id,
            }
        )
        if transaction_type_additional_info is not UNSET:
            field_dict["transactionTypeAdditionalInfo"] = (
                transaction_type_additional_info
            )
        if price_factor is not UNSET:
            field_dict["priceFactor"] = price_factor
        if transaction_unit_price is not UNSET:
            field_dict["transactionUnitPrice"] = transaction_unit_price
        if transaction_quantity is not UNSET:
            field_dict["transactionQuantity"] = transaction_quantity
        if broker_note_id is not UNSET:
            field_dict["brokerNoteId"] = broker_note_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_transactions_current_data_transaction_unit_price import (
            ResponseVariableIncomesTransactionsCurrentDataTransactionUnitPrice,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_transactions_current_data_transaction_value import (
            ResponseVariableIncomesTransactionsCurrentDataTransactionValue,
        )

        d = dict(src_dict)
        type_ = EnumVariableIncomesTransactionsCurrentType(d.pop("type"))

        transaction_type = EnumVariableIncomesTransactionsCurrentTransactionType(
            d.pop("transactionType")
        )

        transaction_date = isoparse(d.pop("transactionDate")).date()

        transaction_value = (
            ResponseVariableIncomesTransactionsCurrentDataTransactionValue.from_dict(
                d.pop("transactionValue")
            )
        )

        transaction_id = d.pop("transactionId")

        transaction_type_additional_info = d.pop("transactionTypeAdditionalInfo", UNSET)

        price_factor = d.pop("priceFactor", UNSET)

        _transaction_unit_price = d.pop("transactionUnitPrice", UNSET)
        transaction_unit_price: (
            'ResponseVariableIncomesTransactionsCurrentDataTransactionUnitPrice | Unset'
        )
        if isinstance(_transaction_unit_price, Unset):
            transaction_unit_price = UNSET
        else:
            transaction_unit_price = ResponseVariableIncomesTransactionsCurrentDataTransactionUnitPrice.from_dict(
                _transaction_unit_price
            )

        transaction_quantity = d.pop("transactionQuantity", UNSET)

        broker_note_id = d.pop("brokerNoteId", UNSET)

        response_variable_incomes_transactions_current_data = cls(
            type_=type_,
            transaction_type=transaction_type,
            transaction_date=transaction_date,
            transaction_value=transaction_value,
            transaction_id=transaction_id,
            transaction_type_additional_info=transaction_type_additional_info,
            price_factor=price_factor,
            transaction_unit_price=transaction_unit_price,
            transaction_quantity=transaction_quantity,
            broker_note_id=broker_note_id,
        )

        return response_variable_incomes_transactions_current_data
