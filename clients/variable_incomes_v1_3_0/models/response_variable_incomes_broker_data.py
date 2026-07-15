"""ResponseVariableIncomesBrokerData: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_brokerage_fee import (
        ResponseVariableIncomesBrokerDataBrokerageFee,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_clearing_custody_fee import (
        ResponseVariableIncomesBrokerDataClearingCustodyFee,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_clearing_registration_fee import (
        ResponseVariableIncomesBrokerDataClearingRegistrationFee,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_clearing_settlement_fee import (
        ResponseVariableIncomesBrokerDataClearingSettlementFee,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_gross_value import (
        ResponseVariableIncomesBrokerDataGrossValue,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_income_tax import (
        ResponseVariableIncomesBrokerDataIncomeTax,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_net_value import (
        ResponseVariableIncomesBrokerDataNetValue,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_stock_exchange_asset_trade_notice_fee import (
        ResponseVariableIncomesBrokerDataStockExchangeAssetTradeNoticeFee,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_stock_exchange_fee import (
        ResponseVariableIncomesBrokerDataStockExchangeFee,
    )
    from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_taxes import (
        ResponseVariableIncomesBrokerDataTaxes,
    )


T = TypeVar("T", bound="ResponseVariableIncomesBrokerData")


@_attrs_define
class ResponseVariableIncomesBrokerData:
    """
    Attributes:
        broker_note_number (str): Identificador da nota de negociação. Não deve ser utilizado como chave na API.
            Example: 1854009930314350.
        gross_value (ResponseVariableIncomesBrokerDataGrossValue): o valor da nota de negociação é o somatório das
            operações realizadas. Total de compra e venda do dia.
        brokerage_fee (ResponseVariableIncomesBrokerDataBrokerageFee): a taxa de corretagem incide sobre o valor bruto
            da nota de negociação, e é livremente pactuada entre o investidor e o seu intermediário.
            Pode ser cobrada como um valor fixo por operação, ou um como um percentual sobre o valor negociado, ou ainda de
            forma mista, conforme guia CVM do investidor.
        clearing_settlement_fee (ResponseVariableIncomesBrokerDataClearingSettlementFee): Valor cobrado para liquidação
            na custódia.
        clearing_registration_fee (ResponseVariableIncomesBrokerDataClearingRegistrationFee): Valor cobrado para
            registro na custódia.
        stock_exchange_asset_trade_notice_fee (ResponseVariableIncomesBrokerDataStockExchangeAssetTradeNoticeFee): Valor
            cobrada pela bolsa pelo aviso de negociação de ativo.
        stock_exchange_fee (ResponseVariableIncomesBrokerDataStockExchangeFee): Valor cobrado pela bolsa para remunerar
            os serviços de registro prestados.
        clearing_custody_fee (ResponseVariableIncomesBrokerDataClearingCustodyFee): Taxa cobrada pelas IF para custódia.
        taxes (ResponseVariableIncomesBrokerDataTaxes): Impostos cobrados na operação, inclusive imposto de renda day-
            trade, exceto imposto de renda retido na fonte.
        income_tax (ResponseVariableIncomesBrokerDataIncomeTax): Imposto de renda retido na fonte.
        net_value (ResponseVariableIncomesBrokerDataNetValue): Valor líquido da nota de negociação após despesas com
            taxa de corretagem, taxa de liquidação, taxa de registro, taxa A.N.A, emolumentos, taxa de custódia, impostos e
            IRRF.
    """

    broker_note_number: str
    gross_value: 'ResponseVariableIncomesBrokerDataGrossValue'
    brokerage_fee: 'ResponseVariableIncomesBrokerDataBrokerageFee'
    clearing_settlement_fee: 'ResponseVariableIncomesBrokerDataClearingSettlementFee'
    clearing_registration_fee: 'ResponseVariableIncomesBrokerDataClearingRegistrationFee'
    stock_exchange_asset_trade_notice_fee: (
        'ResponseVariableIncomesBrokerDataStockExchangeAssetTradeNoticeFee'
    )
    stock_exchange_fee: 'ResponseVariableIncomesBrokerDataStockExchangeFee'
    clearing_custody_fee: 'ResponseVariableIncomesBrokerDataClearingCustodyFee'
    taxes: 'ResponseVariableIncomesBrokerDataTaxes'
    income_tax: 'ResponseVariableIncomesBrokerDataIncomeTax'
    net_value: 'ResponseVariableIncomesBrokerDataNetValue'

    def to_dict(self) -> dict[str, Any]:
        broker_note_number = self.broker_note_number

        gross_value = self.gross_value.to_dict()

        brokerage_fee = self.brokerage_fee.to_dict()

        clearing_settlement_fee = self.clearing_settlement_fee.to_dict()

        clearing_registration_fee = self.clearing_registration_fee.to_dict()

        stock_exchange_asset_trade_notice_fee = (
            self.stock_exchange_asset_trade_notice_fee.to_dict()
        )

        stock_exchange_fee = self.stock_exchange_fee.to_dict()

        clearing_custody_fee = self.clearing_custody_fee.to_dict()

        taxes = self.taxes.to_dict()

        income_tax = self.income_tax.to_dict()

        net_value = self.net_value.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "brokerNoteNumber": broker_note_number,
                "grossValue": gross_value,
                "brokerageFee": brokerage_fee,
                "clearingSettlementFee": clearing_settlement_fee,
                "clearingRegistrationFee": clearing_registration_fee,
                "stockExchangeAssetTradeNoticeFee": stock_exchange_asset_trade_notice_fee,
                "stockExchangeFee": stock_exchange_fee,
                "clearingCustodyFee": clearing_custody_fee,
                "taxes": taxes,
                "incomeTax": income_tax,
                "netValue": net_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_brokerage_fee import (
            ResponseVariableIncomesBrokerDataBrokerageFee,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_clearing_custody_fee import (
            ResponseVariableIncomesBrokerDataClearingCustodyFee,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_clearing_registration_fee import (
            ResponseVariableIncomesBrokerDataClearingRegistrationFee,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_clearing_settlement_fee import (
            ResponseVariableIncomesBrokerDataClearingSettlementFee,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_gross_value import (
            ResponseVariableIncomesBrokerDataGrossValue,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_income_tax import (
            ResponseVariableIncomesBrokerDataIncomeTax,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_net_value import (
            ResponseVariableIncomesBrokerDataNetValue,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_stock_exchange_asset_trade_notice_fee import (
            ResponseVariableIncomesBrokerDataStockExchangeAssetTradeNoticeFee,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_stock_exchange_fee import (
            ResponseVariableIncomesBrokerDataStockExchangeFee,
        )
        from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker_data_taxes import (
            ResponseVariableIncomesBrokerDataTaxes,
        )

        d = dict(src_dict)
        broker_note_number = d.pop("brokerNoteNumber")

        gross_value = ResponseVariableIncomesBrokerDataGrossValue.from_dict(
            d.pop("grossValue")
        )

        brokerage_fee = ResponseVariableIncomesBrokerDataBrokerageFee.from_dict(
            d.pop("brokerageFee")
        )

        clearing_settlement_fee = (
            ResponseVariableIncomesBrokerDataClearingSettlementFee.from_dict(
                d.pop("clearingSettlementFee")
            )
        )

        clearing_registration_fee = (
            ResponseVariableIncomesBrokerDataClearingRegistrationFee.from_dict(
                d.pop("clearingRegistrationFee")
            )
        )

        stock_exchange_asset_trade_notice_fee = (
            ResponseVariableIncomesBrokerDataStockExchangeAssetTradeNoticeFee.from_dict(
                d.pop("stockExchangeAssetTradeNoticeFee")
            )
        )

        stock_exchange_fee = (
            ResponseVariableIncomesBrokerDataStockExchangeFee.from_dict(
                d.pop("stockExchangeFee")
            )
        )

        clearing_custody_fee = (
            ResponseVariableIncomesBrokerDataClearingCustodyFee.from_dict(
                d.pop("clearingCustodyFee")
            )
        )

        taxes = ResponseVariableIncomesBrokerDataTaxes.from_dict(d.pop("taxes"))

        income_tax = ResponseVariableIncomesBrokerDataIncomeTax.from_dict(
            d.pop("incomeTax")
        )

        net_value = ResponseVariableIncomesBrokerDataNetValue.from_dict(
            d.pop("netValue")
        )

        response_variable_incomes_broker_data = cls(
            broker_note_number=broker_note_number,
            gross_value=gross_value,
            brokerage_fee=brokerage_fee,
            clearing_settlement_fee=clearing_settlement_fee,
            clearing_registration_fee=clearing_registration_fee,
            stock_exchange_asset_trade_notice_fee=stock_exchange_asset_trade_notice_fee,
            stock_exchange_fee=stock_exchange_fee,
            clearing_custody_fee=clearing_custody_fee,
            taxes=taxes,
            income_tax=income_tax,
            net_value=net_value,
        )

        return response_variable_incomes_broker_data
