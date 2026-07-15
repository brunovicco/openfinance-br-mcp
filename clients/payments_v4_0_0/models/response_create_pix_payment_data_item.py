"""Payments API model: Objeto contendo dados do pagamento e da conta do recebedor (creditor)."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.payments_v4_0_0.models.enum_local_instrument import EnumLocalInstrument
from clients.payments_v4_0_0.models.enum_payment_status_type import EnumPaymentStatusType
from clients.payments_v4_0_0.models.response_create_pix_payment_data_item_authorisation_flow import (
    ResponseCreatePixPaymentDataItemAuthorisationFlow,
)
from clients.payments_v4_0_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.creditor_account import CreditorAccount
    from clients.payments_v4_0_0.models.debtor_account import DebtorAccount
    from clients.payments_v4_0_0.models.rejection_reason import RejectionReason
    from clients.payments_v4_0_0.models.response_create_pix_payment_data_item_payment import (
        ResponseCreatePixPaymentDataItemPayment,
    )


T = TypeVar("T", bound="ResponseCreatePixPaymentDataItem")


@_attrs_define
class ResponseCreatePixPaymentDataItem:
    """Objeto contendo dados do pagamento e da conta do recebedor (creditor).

    Attributes:
        payment_id (str): Código ou identificador único informado pela instituição detentora da conta para representar
            a iniciação de pagamento individual. O `paymentId` deve ser diferente do `endToEndId`.
            Este é o identificador que deverá ser utilizado na consulta ao status da iniciação de pagamento efetuada.
             Example: TXpRMU9UQTROMWhZV2xSU1FUazJSMDl.
        end_to_end_id (str): Trata-se de um identificador único, gerado na instituição iniciadora de pagamento e
            recebido na instituição detentora de conta, permeando toda a jornada do pagamento Pix.

            [Restrição] A detentora deve obrigatoriamente retornar o campo Com o mesmo valor recebido da iniciadora.
             Example: E9040088820210128000800123873170.
        creation_date_time (datetime.datetime): Data e hora em que o recurso foi criado.
            Uma string com data e hora conforme especificação RFC-3339,
            sempre com a utilização de timezone UTC(UTC time format).
             Example: 2020-07-21T08:30:00Z.
        status_update_date_time (datetime.datetime): Data e hora da última atualização da iniciação de pagamento.
            Uma string com data e hora conforme especificação RFC-3339,
            sempre com a utilização de timezone UTC(UTC time format).
             Example: 2020-07-21T08:30:00Z.
        status (EnumPaymentStatusType): Estado atual da iniciação de pagamento. O estado evolui na seguinte ordem:

            1.  RCVD (Received) - Indica que a requisição de pagamento foi recebida com sucesso pela detentora, mas ainda há
            validações a serem feitas antes de ser submetida para liquidação.

            2.  CANC (Cancelled) - Indica que a transação Pix pendente foi cancelada com sucesso pelo usuário antes que
            fosse confirmada (ACCP) ou rejeitada (RJCT) pela detentora.

            3.  ACCP( Accepted Customer Profile) - Indica que todas as verificações necessárias já foram realizadas pela
            detentora e que a transação está pronta para ser enviada para liquidação (no SPI se for Pix para outra
            instituição ou internamente se for para outra conta na mesma instituição).

            4.  ACPD (Accepted Clearing Processed) - Indica que a detentora já submeteu a transação para liquidação, mas
            ainda não tem a confirmação se foi liquidada ou rejeitada.

            5.  RJCT (Rejected) Indica que a transação foi rejeitada pela detentora ou pelo SPI.

            6.  ACSC (Accepted Settlement Completed Debitor Account) - Indica que a transação foi efetivada pela detentora
            ou pelo SPI.

            7.  PDNG (Pending) - Indica que a detentora reteve temporariamente a transação Pix para análise.

            8.  SCHD (Scheduled) - Indica que a transação Pix foi agendada com sucesso na detentora.

            Em caso insucesso:

            RJCT (REJECTED) - Instrução de pagamento rejeitada.
             Example: PDNG.
        local_instrument (EnumLocalInstrument): Especifica a forma de iniciação do pagamento:
            - MANU - Inserção manual de dados da conta transacional
            - DICT - Inserção manual de chave Pix
            - QRDN - QR code dinâmico
            - QRES - QR code estático
            - INIC - Indica que o recebedor (creditor) contratou o Iniciador de Pagamentos especificamente para realizar
            iniciações de pagamento em que o beneficiário é previamente conhecido.

            [Restrição] Se /data/payment/schedule enviado com valor diferente de single durante a criação do consentimento,
            apenas os métodos MANU, DICT ou QRES são permitidos.
             Example: DICT.
        cnpj_initiator (str): CNPJ do Iniciador de Pagamento devidamente habilitado para a prestação de Serviço de
            Iniciação no Pix. Example: 50685362000135.
        payment (ResponseCreatePixPaymentDataItemPayment): Objeto contendo dados do pagameto como moeda e valor.
        creditor_account (CreditorAccount): Objeto que contém a identificação da conta de destino do
            beneficiário/recebedor.
        debtor_account (DebtorAccount): Objeto que contém a identificação da conta de origem do pagador.
            As informações quanto à conta de origem do pagador poderão ser trazidas no consentimento para a detentora, caso
            a iniciadora tenha coletado essas informações do cliente. Do contrário, será coletada na detentora e trazida
            para a iniciadora como resposta à criação do pagamento.
        consent_id (str | Unset): Identificador único do consentimento criado para a iniciação de pagamento solicitada.
            Deverá ser um URN - Uniform Resource Name.
            Um URN, conforme definido na [RFC8141](https://tools.ietf.org/html/rfc8141) é um Uniform Resource
            Identifier - URI - que é atribuído sob o URI scheme "urn" e um namespace URN específico, com a intenção de que o
            URN
            seja um identificador de recurso persistente e independente da localização.
            Considerando a string urn:bancoex:C1DD33123 como exemplo para consentId temos:
            - o namespace(urn)
            - o identificador associado ao namespace da instituição transnmissora (bancoex)
            - o identificador específico dentro do namespace (C1DD33123).
            Informações mais detalhadas sobre a construção de namespaces devem ser consultadas na
            [RFC8141](https://tools.ietf.org/html/rfc8141).

            [Restrição] Este campo é de preenchimento obrigatório quando o valor do campo authorisationFlow for igual a
            FIDO_FLOW.
             Example: urn:bancoex:C1DD33123.
        proxy (str | Unset): Chave cadastrada no DICT pertencente ao recebedor. Os tipos de chaves podem ser: telefone,
            e-mail, cpf/cnpj ou chave aleatória.
            No caso de telefone celular deve ser informado no padrão E.1641.
            Para e-mail deve ter o formato xxxxxxxx@xxxxxxx.xxx(.xx) e no máximo 77 caracteres.
            No caso de CPF deverá ser informado com 11 números, sem pontos ou traços.
            Para o caso de CNPJ deverá ser informado com 14 números, sem pontos ou traços.
            No caso de chave aleatória deve ser informado o UUID gerado pelo DICT, conforme formato especificado na
            RFC41223.
            Se informado, a detentora da conta deve validar o proxy no DICT quando localInstrument for igual a DICT, QRDN ou
            QRES e validar o campo creditorAccount.
            Esta validação é opcional caso o localInstrument for igual a INIC.
            [Restrição] Se localInstrument for igual a MANU, o campo proxy não deve ser preenchido. Se localInstrument for
            igual INIC, DICT, QRDN ou QRES, o campo proxy deve ser sempre preenchido com a chave Pix.
             Example: 12345678901.
        ibge_town_code (str | Unset): O campo ibgetowncode no arranjo PIX, tem o mesmo comportamento que o campo codMun
            descrito no item 1.6.6 do manual do PIX, conforme segue:

            1. Caso a informação referente ao município não seja enviada; o PSP do recebedor assumirá que não existem
            feriados estaduais e municipais no período em questão;
             Example: 5300108.
        rejection_reason (RejectionReason | Unset): Motivo da rejeição do pagamento. Informações complementares sobre o
            motivo do status
            [Restrição] Esse motivo deverá ser enviado quando o campo /data/status for igual a RJCT (REJECTED).
        transaction_identification (str | Unset): Trata-se de um identificador de transação que deve ser retransmitido
            intacto pelo PSP do pagador ao gerar a ordem de pagamento.

            [Restrição] A detentora deve obrigatoriamente retornar o campo com o mesmo valor recebido da iniciadora, caso
            ele tenha sido enviado na requisição da iniciação do pagamento.
             Example: E00038166201907261559y6j6.
        remittance_information (str | Unset): Deve ser preenchido sempre que o usuário pagador inserir alguma informação
            adicional em um pagamento, a ser enviada ao recebedor.
             Example: Pagamento da nota RSTO035-002..
        authorisation_flow (ResponseCreatePixPaymentDataItemAuthorisationFlow | Unset): Campo condicional utilizado para
            identificar o fluxo de autorização em que o pagamento foi solicitado.

            [Restrição] Se CIBA ou FIDO, preenchimento obrigatório. Caso o campo não esteja presente no payload, subentende-
            se que o fluxo de autorização utilizado é o HYBRID_FLOW.
             Example: HYBRID_FLOW.
    """

    payment_id: str
    end_to_end_id: str
    creation_date_time: datetime.datetime
    status_update_date_time: datetime.datetime
    status: EnumPaymentStatusType
    local_instrument: EnumLocalInstrument
    cnpj_initiator: str
    payment: 'ResponseCreatePixPaymentDataItemPayment'
    creditor_account: 'CreditorAccount'
    debtor_account: 'DebtorAccount'
    consent_id: str | Unset = UNSET
    proxy: str | Unset = UNSET
    ibge_town_code: str | Unset = UNSET
    rejection_reason: 'RejectionReason | Unset' = UNSET
    transaction_identification: str | Unset = UNSET
    remittance_information: str | Unset = UNSET
    authorisation_flow: ResponseCreatePixPaymentDataItemAuthorisationFlow | Unset = (
        UNSET
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payment_id = self.payment_id

        end_to_end_id = self.end_to_end_id

        creation_date_time = self.creation_date_time.isoformat()

        status_update_date_time = self.status_update_date_time.isoformat()

        status = self.status.value

        local_instrument = self.local_instrument.value

        cnpj_initiator = self.cnpj_initiator

        payment = self.payment.to_dict()

        creditor_account = self.creditor_account.to_dict()

        debtor_account = self.debtor_account.to_dict()

        consent_id = self.consent_id

        proxy = self.proxy

        ibge_town_code = self.ibge_town_code

        rejection_reason: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rejection_reason, Unset):
            rejection_reason = self.rejection_reason.to_dict()

        transaction_identification = self.transaction_identification

        remittance_information = self.remittance_information

        authorisation_flow: str | Unset = UNSET
        if not isinstance(self.authorisation_flow, Unset):
            authorisation_flow = self.authorisation_flow.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paymentId": payment_id,
                "endToEndId": end_to_end_id,
                "creationDateTime": creation_date_time,
                "statusUpdateDateTime": status_update_date_time,
                "status": status,
                "localInstrument": local_instrument,
                "cnpjInitiator": cnpj_initiator,
                "payment": payment,
                "creditorAccount": creditor_account,
                "debtorAccount": debtor_account,
            }
        )
        if consent_id is not UNSET:
            field_dict["consentId"] = consent_id
        if proxy is not UNSET:
            field_dict["proxy"] = proxy
        if ibge_town_code is not UNSET:
            field_dict["ibgeTownCode"] = ibge_town_code
        if rejection_reason is not UNSET:
            field_dict["rejectionReason"] = rejection_reason
        if transaction_identification is not UNSET:
            field_dict["transactionIdentification"] = transaction_identification
        if remittance_information is not UNSET:
            field_dict["remittanceInformation"] = remittance_information
        if authorisation_flow is not UNSET:
            field_dict["authorisationFlow"] = authorisation_flow

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.creditor_account import CreditorAccount
        from clients.payments_v4_0_0.models.debtor_account import DebtorAccount
        from clients.payments_v4_0_0.models.rejection_reason import RejectionReason
        from clients.payments_v4_0_0.models.response_create_pix_payment_data_item_payment import (
            ResponseCreatePixPaymentDataItemPayment,
        )

        d = dict(src_dict)
        payment_id = d.pop("paymentId")

        end_to_end_id = d.pop("endToEndId")

        creation_date_time = isoparse(d.pop("creationDateTime"))

        status_update_date_time = isoparse(d.pop("statusUpdateDateTime"))

        status = EnumPaymentStatusType(d.pop("status"))

        local_instrument = EnumLocalInstrument(d.pop("localInstrument"))

        cnpj_initiator = d.pop("cnpjInitiator")

        payment = ResponseCreatePixPaymentDataItemPayment.from_dict(d.pop("payment"))

        creditor_account = CreditorAccount.from_dict(d.pop("creditorAccount"))

        debtor_account = DebtorAccount.from_dict(d.pop("debtorAccount"))

        consent_id = d.pop("consentId", UNSET)

        proxy = d.pop("proxy", UNSET)

        ibge_town_code = d.pop("ibgeTownCode", UNSET)

        _rejection_reason = d.pop("rejectionReason", UNSET)
        rejection_reason: 'RejectionReason | Unset'
        if isinstance(_rejection_reason, Unset):
            rejection_reason = UNSET
        else:
            rejection_reason = RejectionReason.from_dict(_rejection_reason)

        transaction_identification = d.pop("transactionIdentification", UNSET)

        remittance_information = d.pop("remittanceInformation", UNSET)

        _authorisation_flow = d.pop("authorisationFlow", UNSET)
        authorisation_flow: ResponseCreatePixPaymentDataItemAuthorisationFlow | Unset
        if isinstance(_authorisation_flow, Unset):
            authorisation_flow = UNSET
        else:
            authorisation_flow = ResponseCreatePixPaymentDataItemAuthorisationFlow(
                _authorisation_flow
            )

        response_create_pix_payment_data_item = cls(
            payment_id=payment_id,
            end_to_end_id=end_to_end_id,
            creation_date_time=creation_date_time,
            status_update_date_time=status_update_date_time,
            status=status,
            local_instrument=local_instrument,
            cnpj_initiator=cnpj_initiator,
            payment=payment,
            creditor_account=creditor_account,
            debtor_account=debtor_account,
            consent_id=consent_id,
            proxy=proxy,
            ibge_town_code=ibge_town_code,
            rejection_reason=rejection_reason,
            transaction_identification=transaction_identification,
            remittance_information=remittance_information,
            authorisation_flow=authorisation_flow,
        )

        response_create_pix_payment_data_item.additional_properties = d
        return response_create_pix_payment_data_item

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
