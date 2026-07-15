"""Credit Cards Accounts API model: Lista que traz os valores relativos aos saldos do Limite de crédito total da conta de pagamento pós-paga"""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.credit_cards_v2_3_1.models.enum_credit_card_account_fee import EnumCreditCardAccountFee
from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_other_credit_type import (
    EnumCreditCardAccountsOtherCreditType,
)
from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_payment_type import (
    EnumCreditCardAccountsPaymentType,
)
from clients.credit_cards_v2_3_1.models.enum_credit_card_transaction_type import EnumCreditCardTransactionType
from clients.credit_cards_v2_3_1.models.enum_credit_debit_indicator import EnumCreditDebitIndicator
from clients.credit_cards_v2_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.credit_cards_v2_3_1.models.credit_card_accounts_transaction_amount import (
        CreditCardAccountsTransactionAmount,
    )
    from clients.credit_cards_v2_3_1.models.credit_card_accounts_transaction_brazilian_amount import (
        CreditCardAccountsTransactionBrazilianAmount,
    )


T = TypeVar("T", bound="CreditCardAccountsBillsTransactions")


@_attrs_define
class CreditCardAccountsBillsTransactions:
    """Lista que traz os valores relativos aos saldos do Limite de crédito total da conta de pagamento pós-paga

    Attributes:
        transaction_id (str): Código ou identificador único prestado pela instituição que mantém a conta para
            representar a transação individual.
            É esperado que o `transactionId` seja único, imutável e estável.
             Example: TXpRMU9UQTROMWhZV2xSU1FUazJSMDl.
        identification_number (str): Número de identificação do cartão: corresponde aos 4 últimos dígitos do cartão para
            PF, ou então, preencher com um identificador para PJ, com as caracteristicas definidas para os IDs no Open
            Finance.
             Example: 4453.
        transaction_name (str): Literal usada na instituição financeira para identificar a transação. A informação
            apresentada precisa ser a mesma utilizada nos canais eletrônicos da instituição (extrato e fatura). Example:
            PGTO.
        credit_debit_type (EnumCreditDebitIndicator): Indicador do tipo de lançamento:
            Débito (no extrato) Em um extrato bancário, os débitos, marcados com a letra “D” ao lado do valor registrado,
            informam as saídas de dinheiro na conta-corrente.
            Crédito (no extrato) Em um extrato bancário, os créditos, marcados com a letra “C” ao lado do valor registrado,
            informam as entradas de dinheiro na conta-corrente.
             Example: DEBITO.
        transaction_type (EnumCreditCardTransactionType): Traz os tipos de Transação Example: CASHBACK.
        brazilian_amount (CreditCardAccountsTransactionBrazilianAmount): Valor da transação expresso em valor monetário
            com no mínimo 2 casas e no máximo 4 casas decimais, em moeda corrente do Brasil. Deve ser o valor de amount
            convertido para BRL (em caso de compra internacional) ou o mesmo valor de amount (em caso de compra nacional).
        amount (CreditCardAccountsTransactionAmount): Valor original da transação. Expresso em valor monetário com no
            mínimo 2 casas decimais e no máximo 4 casas decimais. Deve ser sempre preenchido com o valor original da
            transação independente da nacionalidade, sem convertê-lo.
        transaction_date_time (datetime.datetime): Data e hora da transação disponível para os clientes nos canais
            digitais da instituição. Neste momento, é obrigatório preencher com dados reais com precisão de data, hora e
            minuto, mesmo que a instituição não exiba para o cliente nesse nível de granularidade, em algumas situações.
            Dessa forma, os segundos e milissegundos podem ser preenchidos com zero (0), por exemplo:
            2024-01-29T11:15:00.000Z.
             Example: 2016-01-29T12:29:03.374Z.
        bill_post_date (datetime.date): Data em que a transação foi inserida na fatura Example: 2021-05-21.
        bill_id (str | Unset): Informação que identifica a fatura onde consta a transação informada. Example:
            MTU0OTU1NjI2NTk4OTRmc2ZhZDRmc2Q1NmZkM.
        transactional_additional_info (str | Unset): Campo livre, de preenchimento obrigatório quando selecionado tipo
            de transação "OUTROS"
        payment_type (EnumCreditCardAccountsPaymentType | Unset): Traz os tipos de pagamento.

            [Restrição] Preenchimento obrigatório se Tipo de Transação selecionada for 'PAGAMENTO'.
             Example: A_VISTA.
        fee_type (EnumCreditCardAccountFee | Unset): Traz os tipos de Tarifas: (Vide Enum) Anuidade, Saque com cartão no
            Brasil, Saque com cartão no exterior, Avaliação emergencial de crédito, Emissão segunda via, Tarifa pagamento de
            contas, SMS, OUTRA.

            [Restrição] Preenchimento obrigatório se Tipo de Transação selecionada for 'TARIFA'.
             Example: ANUIDADE.
        fee_type_additional_info (str | Unset): Campo livre, de preenchimento obrigatório quando selecionada tipo de
            tarifa "OUTRA"
        other_credits_type (EnumCreditCardAccountsOtherCreditType | Unset): Traz outros tipos de crédito contratados no
            cartão.

            [Restrição] Preenchimento obrigatório se o tipo transação selecionado for
            'OPERACOES_CREDITO_CONTRATADAS_CARTAO'.
             Example: CREDITO_ROTATIVO.
        other_credits_additional_info (str | Unset): Campo livre para preenchimento de dados adicionais de outros tipos
            de crédito contratados no cartão.

            [Restrição] Preenchimento obrigatório quando selecionado no campo outros tipos de crédito "OUTROS".
        charge_identificator (float | Unset): Número da parcela que está sendo informada.

            [Restrição] Preenchimento obrigatório se Tipo de Pagamento (paymentType) selecionada for 'A_PRAZO'.
             Example: 12.
        charge_number (float | Unset): Quantidade de parcelas.
            [Restrição] O campo deve ser preenchido quando houverem parcelas relacionadas a transação.
             Example: 12.
        payee_mcc (float | Unset): O MCC ou o código da categoria do estabelecimento comercial. Os MCCs são agrupados
            segundo suas similaridades. O MCC é usado para classificar o negócio pelo tipo fornecido de bens ou serviços. Os
            MCCs são atribuídos por tipo de comerciante (por exemplo, um para hotéis, um para lojas de materiais de
            escritório, etc.) ou por nome de comerciante (por exemplo, 3000 para a United Airlines).
             Example: 5137.
    """

    transaction_id: str
    identification_number: str
    transaction_name: str
    credit_debit_type: EnumCreditDebitIndicator
    transaction_type: EnumCreditCardTransactionType
    brazilian_amount: 'CreditCardAccountsTransactionBrazilianAmount'
    amount: 'CreditCardAccountsTransactionAmount'
    transaction_date_time: datetime.datetime
    bill_post_date: datetime.date
    bill_id: str | Unset = UNSET
    transactional_additional_info: str | Unset = UNSET
    payment_type: EnumCreditCardAccountsPaymentType | Unset = UNSET
    fee_type: EnumCreditCardAccountFee | Unset = UNSET
    fee_type_additional_info: str | Unset = UNSET
    other_credits_type: EnumCreditCardAccountsOtherCreditType | Unset = UNSET
    other_credits_additional_info: str | Unset = UNSET
    charge_identificator: float | Unset = UNSET
    charge_number: float | Unset = UNSET
    payee_mcc: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        transaction_id = self.transaction_id

        identification_number = self.identification_number

        transaction_name = self.transaction_name

        credit_debit_type = self.credit_debit_type.value

        transaction_type = self.transaction_type.value

        brazilian_amount = self.brazilian_amount.to_dict()

        amount = self.amount.to_dict()

        transaction_date_time = self.transaction_date_time.isoformat()

        bill_post_date = self.bill_post_date.isoformat()

        bill_id = self.bill_id

        transactional_additional_info = self.transactional_additional_info

        payment_type: str | Unset = UNSET
        if not isinstance(self.payment_type, Unset):
            payment_type = self.payment_type.value

        fee_type: str | Unset = UNSET
        if not isinstance(self.fee_type, Unset):
            fee_type = self.fee_type.value

        fee_type_additional_info = self.fee_type_additional_info

        other_credits_type: str | Unset = UNSET
        if not isinstance(self.other_credits_type, Unset):
            other_credits_type = self.other_credits_type.value

        other_credits_additional_info = self.other_credits_additional_info

        charge_identificator = self.charge_identificator

        charge_number = self.charge_number

        payee_mcc = self.payee_mcc

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transactionId": transaction_id,
                "identificationNumber": identification_number,
                "transactionName": transaction_name,
                "creditDebitType": credit_debit_type,
                "transactionType": transaction_type,
                "brazilianAmount": brazilian_amount,
                "amount": amount,
                "transactionDateTime": transaction_date_time,
                "billPostDate": bill_post_date,
            }
        )
        if bill_id is not UNSET:
            field_dict["billId"] = bill_id
        if transactional_additional_info is not UNSET:
            field_dict["transactionalAdditionalInfo"] = transactional_additional_info
        if payment_type is not UNSET:
            field_dict["paymentType"] = payment_type
        if fee_type is not UNSET:
            field_dict["feeType"] = fee_type
        if fee_type_additional_info is not UNSET:
            field_dict["feeTypeAdditionalInfo"] = fee_type_additional_info
        if other_credits_type is not UNSET:
            field_dict["otherCreditsType"] = other_credits_type
        if other_credits_additional_info is not UNSET:
            field_dict["otherCreditsAdditionalInfo"] = other_credits_additional_info
        if charge_identificator is not UNSET:
            field_dict["chargeIdentificator"] = charge_identificator
        if charge_number is not UNSET:
            field_dict["chargeNumber"] = charge_number
        if payee_mcc is not UNSET:
            field_dict["payeeMCC"] = payee_mcc

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.credit_cards_v2_3_1.models.credit_card_accounts_transaction_amount import (
            CreditCardAccountsTransactionAmount,
        )
        from clients.credit_cards_v2_3_1.models.credit_card_accounts_transaction_brazilian_amount import (
            CreditCardAccountsTransactionBrazilianAmount,
        )

        d = dict(src_dict)
        transaction_id = d.pop("transactionId")

        identification_number = d.pop("identificationNumber")

        transaction_name = d.pop("transactionName")

        credit_debit_type = EnumCreditDebitIndicator(d.pop("creditDebitType"))

        transaction_type = EnumCreditCardTransactionType(d.pop("transactionType"))

        brazilian_amount = CreditCardAccountsTransactionBrazilianAmount.from_dict(
            d.pop("brazilianAmount")
        )

        amount = CreditCardAccountsTransactionAmount.from_dict(d.pop("amount"))

        transaction_date_time = isoparse(d.pop("transactionDateTime"))

        bill_post_date = isoparse(d.pop("billPostDate")).date()

        bill_id = d.pop("billId", UNSET)

        transactional_additional_info = d.pop("transactionalAdditionalInfo", UNSET)

        _payment_type = d.pop("paymentType", UNSET)
        payment_type: EnumCreditCardAccountsPaymentType | Unset
        if isinstance(_payment_type, Unset):
            payment_type = UNSET
        else:
            payment_type = EnumCreditCardAccountsPaymentType(_payment_type)

        _fee_type = d.pop("feeType", UNSET)
        fee_type: EnumCreditCardAccountFee | Unset
        if isinstance(_fee_type, Unset):
            fee_type = UNSET
        else:
            fee_type = EnumCreditCardAccountFee(_fee_type)

        fee_type_additional_info = d.pop("feeTypeAdditionalInfo", UNSET)

        _other_credits_type = d.pop("otherCreditsType", UNSET)
        other_credits_type: EnumCreditCardAccountsOtherCreditType | Unset
        if isinstance(_other_credits_type, Unset):
            other_credits_type = UNSET
        else:
            other_credits_type = EnumCreditCardAccountsOtherCreditType(
                _other_credits_type
            )

        other_credits_additional_info = d.pop("otherCreditsAdditionalInfo", UNSET)

        charge_identificator = d.pop("chargeIdentificator", UNSET)

        charge_number = d.pop("chargeNumber", UNSET)

        payee_mcc = d.pop("payeeMCC", UNSET)

        credit_card_accounts_bills_transactions = cls(
            transaction_id=transaction_id,
            identification_number=identification_number,
            transaction_name=transaction_name,
            credit_debit_type=credit_debit_type,
            transaction_type=transaction_type,
            brazilian_amount=brazilian_amount,
            amount=amount,
            transaction_date_time=transaction_date_time,
            bill_post_date=bill_post_date,
            bill_id=bill_id,
            transactional_additional_info=transactional_additional_info,
            payment_type=payment_type,
            fee_type=fee_type,
            fee_type_additional_info=fee_type_additional_info,
            other_credits_type=other_credits_type,
            other_credits_additional_info=other_credits_additional_info,
            charge_identificator=charge_identificator,
            charge_number=charge_number,
            payee_mcc=payee_mcc,
        )

        credit_card_accounts_bills_transactions.additional_properties = d
        return credit_card_accounts_bills_transactions

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
