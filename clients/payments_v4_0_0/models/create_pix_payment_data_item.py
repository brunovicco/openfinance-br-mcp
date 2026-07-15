"""Payments API model: Objeto contendo dados do pagamento e do recebedor (creditor)."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.create_pix_payment_data_item_authorisation_flow import (
    CreatePixPaymentDataItemAuthorisationFlow,
)
from clients.payments_v4_0_0.models.enum_local_instrument import EnumLocalInstrument
from clients.payments_v4_0_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.creditor_account import CreditorAccount
    from clients.payments_v4_0_0.models.payment_pix import PaymentPix


T = TypeVar("T", bound="CreatePixPaymentDataItem")


@_attrs_define
class CreatePixPaymentDataItem:
    """Objeto contendo dados do pagamento e do recebedor (creditor).

    Attributes:
        end_to_end_id (str): Deve ser preenchido no formato padrão ExxxxxxxxyyyyMMddHHmmkkkkkkkkkkk (32 caracteres;
            “case sensitive”, isso é, diferencia letras maiúsculas e minúsculas), sendo:

            • “E” – fixo (1 caractere);

            • xxxxxxxx – identificação do agente que gerou o ´EndToEndId´, podendo ser: o ISPB do participante direto ou o
            ISPB do participante indireto (8 caracteres numéricos [0-9]);

            • yyyyMMddHHmm – data, hora e minuto (12 caracteres), seguindo o horário UTC, da submissão da ordem de
            pagamento, caso a liquidação seja prioritária, ou prevista para o envio da ordem ao sistema de liquidação, caso
            seja realizado um agendamento. Para ordens prioritárias e não prioritárias, aceita-se o preenchimento, pelo
            agente que gerou o ´EndToEndId´, com uma tolerância máxima de 12 horas, para o futuro e para o passado, em
            relação ao horário efetivo de processamento da ordem pelo SPI;

            • kkkkkkkkkkk – sequencial criado pelo agente que gerou o ´EndToEndId´ (11 caracteres alfanuméricos
            [a-z/A-Z/0-9]). Deve ser único dentro de cada “yyyyMMddHHmm”.

            Admite-se que o ´EndToEndId´ seja gerado pelo participante direto, pelo participante indireto ou pelo iniciador
            de pagamento.

            Ele deve ser único, não podendo ser repetido em qualquer outra operação enviada ao SPI.

            No caso de Pix agendamento, a iniciadora deverá, no que tange a composição do endToEndId, utilizar a data para a
            qual o Pix está sendo agendado e horário fixo 15:00 UTC, que dará para a detentora a janela de efetivação de
            00:00 e 23:59 do horário de Brasília.
             Example: E9040088820210128000800123873170.
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
        payment (PaymentPix): Objeto contendo dados do pagameto como moeda e valor.
        creditor_account (CreditorAccount): Objeto que contém a identificação da conta de destino do
            beneficiário/recebedor.
        cnpj_initiator (str): CNPJ do Iniciador de Pagamento devidamente habilitado para a prestação de Serviço de
            Iniciação no Pix. Example: 50685362000135.
        remittance_information (str | Unset): Deve ser preenchido sempre que o usuário pagador inserir alguma informação
            adicional em um pagamento, a ser enviada ao recebedor.
             Example: Pagamento da nota XPTO035-002..
        qr_code (str | Unset): Sequência de caracteres que corresponde ao QR Code disponibilizado para o pagador.
            É a sequência de caracteres que seria lida pelo leitor de QR Code, e deve propiciar o retorno dos dados do
            pagador após consulta na DICT.
            Essa funcionalidade é possível tanto para QR Code estático quanto para QR Code dinâmico.
            No arranjo do Pix esta é a mesma sequência gerada e/ou lida pela funcionalidade Pix Copia e Cola.
            Este campo deverá ser no formato UTF-8.
            [Restrição] Preenchimento obrigatório para pagamentos por QR Code, observado o tamanho máximo de 512 bytes.
             Example: 00020104141234567890123426660014BR.GOV.BCB.PIX014466756C616E6F32303139406578616D706C652E636F6D27300012
            BR.COM.OUTRO011001234567895204000053039865406123.455802BR5915NOMEDORECEBEDOR6008BRASILIA61087007490062
            530515RP12345678-201950300017BR.GOV.BCB.BRCODE01051.0.080450014BR.GOV.BCB.PIX0123PADRAO.URL.PIX/0123AB
            CD81390012BR.COM.OUTRO01190123.ABCD.3456.WXYZ6304EB76
            .
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
        transaction_identification (str | Unset): Trata-se de um identificador de transação que deve ser retransmitido
            intacto pelo PSP do pagador ao gerar a ordem de pagamento. Essa informação permitirá ao recebedor identificar e
            correlacionar a transferência, quando recebida, com a apresentação das instruções ao pagador.
            Os caracteres permitidos no contexto do Pix para o campo txid (EMV 62-05) são:
            - Letras minúsculas, de ‘a’ a ‘z’
            - Letras maiúsculas, de ‘A’ a ‘z’
            - Dígitos decimais, de ‘0’ a ‘9’

            [Restrição] Preenchimento condicional de acordo com o conteúdo do campo localInstument:

            – MANU - O campo transactionIdentification não deve ser preenchido.
            – DICT - O campo transactionIdentification não deve ser preenchido.
            – INIC - O campo transactionIdentification deve ser preenchido obrigatoriamente e deve conter até 25 caracteres
            alfanuméricos ([a-z|A-Z|0-9]).
            – QRES - Caso o QR Code estático possua o dado <i><<i/>TxId<i>><i/> preenchido, o campo
            transactionIdentification deverá ser preenchido com este valor, caso o QR Code não possua o <i><<i/>TxId<i>><i/>
            o campo transactionIdentification não deverá ser preenchido. O <i><<i/>TxId<i>><i/> deve conter até 25
            caracteres alfanuméricos ([a-z|A-Z|0-9]).
            – QRDN - Será obrigatório seu preenchimento com o <i><<i/>TxId<i>><i/> do payload JSON do QR Code dinâmico. O
            <i><<i/>TxId<i>><i/> deve conter entre 26 e 35 caracteres alfanuméricos ([a-z|A-Z|0-9]).

            A detentora de conta deve validar se a condicionalidade e o formato do campo foram atendidas pela iniciadora de
            pagamento.
             Example: E00038166201907261559y6j6.
        ibge_town_code (str | Unset): O campo ibgetowncode no arranjo PIX, tem o mesmo comportamento que o campo codMun
            descrito no item 1.6.6 do manual do PIX, conforme segue:

            1. Caso a informação referente ao município não seja enviada; o PSP do recebedor assumirá que não existem
            feriados estaduais e municipais no período em questão;
             Example: 5300108.
        authorisation_flow (CreatePixPaymentDataItemAuthorisationFlow | Unset): Campo condicional utilizado para
            identificar o fluxo de autorização em que o pagamento foi solicitado.

            [Restrição] Se CIBA ou FIDO, preenchimento obrigatório. Caso o campo não esteja presente no payload, subentende-
            se que o fluxo de autorização utilizado é o HYBRID_FLOW.
             Example: HYBRID_FLOW.
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
    """

    end_to_end_id: str
    local_instrument: EnumLocalInstrument
    payment: 'PaymentPix'
    creditor_account: 'CreditorAccount'
    cnpj_initiator: str
    remittance_information: str | Unset = UNSET
    qr_code: str | Unset = UNSET
    proxy: str | Unset = UNSET
    transaction_identification: str | Unset = UNSET
    ibge_town_code: str | Unset = UNSET
    authorisation_flow: CreatePixPaymentDataItemAuthorisationFlow | Unset = UNSET
    consent_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        end_to_end_id = self.end_to_end_id

        local_instrument = self.local_instrument.value

        payment = self.payment.to_dict()

        creditor_account = self.creditor_account.to_dict()

        cnpj_initiator = self.cnpj_initiator

        remittance_information = self.remittance_information

        qr_code = self.qr_code

        proxy = self.proxy

        transaction_identification = self.transaction_identification

        ibge_town_code = self.ibge_town_code

        authorisation_flow: str | Unset = UNSET
        if not isinstance(self.authorisation_flow, Unset):
            authorisation_flow = self.authorisation_flow.value

        consent_id = self.consent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "endToEndId": end_to_end_id,
                "localInstrument": local_instrument,
                "payment": payment,
                "creditorAccount": creditor_account,
                "cnpjInitiator": cnpj_initiator,
            }
        )
        if remittance_information is not UNSET:
            field_dict["remittanceInformation"] = remittance_information
        if qr_code is not UNSET:
            field_dict["qrCode"] = qr_code
        if proxy is not UNSET:
            field_dict["proxy"] = proxy
        if transaction_identification is not UNSET:
            field_dict["transactionIdentification"] = transaction_identification
        if ibge_town_code is not UNSET:
            field_dict["ibgeTownCode"] = ibge_town_code
        if authorisation_flow is not UNSET:
            field_dict["authorisationFlow"] = authorisation_flow
        if consent_id is not UNSET:
            field_dict["consentId"] = consent_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.creditor_account import CreditorAccount
        from clients.payments_v4_0_0.models.payment_pix import PaymentPix

        d = dict(src_dict)
        end_to_end_id = d.pop("endToEndId")

        local_instrument = EnumLocalInstrument(d.pop("localInstrument"))

        payment = PaymentPix.from_dict(d.pop("payment"))

        creditor_account = CreditorAccount.from_dict(d.pop("creditorAccount"))

        cnpj_initiator = d.pop("cnpjInitiator")

        remittance_information = d.pop("remittanceInformation", UNSET)

        qr_code = d.pop("qrCode", UNSET)

        proxy = d.pop("proxy", UNSET)

        transaction_identification = d.pop("transactionIdentification", UNSET)

        ibge_town_code = d.pop("ibgeTownCode", UNSET)

        _authorisation_flow = d.pop("authorisationFlow", UNSET)
        authorisation_flow: CreatePixPaymentDataItemAuthorisationFlow | Unset
        if isinstance(_authorisation_flow, Unset):
            authorisation_flow = UNSET
        else:
            authorisation_flow = CreatePixPaymentDataItemAuthorisationFlow(
                _authorisation_flow
            )

        consent_id = d.pop("consentId", UNSET)

        create_pix_payment_data_item = cls(
            end_to_end_id=end_to_end_id,
            local_instrument=local_instrument,
            payment=payment,
            creditor_account=creditor_account,
            cnpj_initiator=cnpj_initiator,
            remittance_information=remittance_information,
            qr_code=qr_code,
            proxy=proxy,
            transaction_identification=transaction_identification,
            ibge_town_code=ibge_town_code,
            authorisation_flow=authorisation_flow,
            consent_id=consent_id,
        )

        create_pix_payment_data_item.additional_properties = d
        return create_pix_payment_data_item

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
