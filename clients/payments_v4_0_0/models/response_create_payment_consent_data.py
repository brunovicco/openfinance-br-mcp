"""Payments API model: Objeto contendo as informações de consentimento para a iniciação de pagamento."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.payments_v4_0_0.models.enum_authorisation_status_type import EnumAuthorisationStatusType
from clients.payments_v4_0_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.business_entity import BusinessEntity
    from clients.payments_v4_0_0.models.consents_debtor_account import ConsentsDebtorAccount
    from clients.payments_v4_0_0.models.identification import Identification
    from clients.payments_v4_0_0.models.logged_user import LoggedUser
    from clients.payments_v4_0_0.models.response_create_payment_consent_data_payment import (
        ResponseCreatePaymentConsentDataPayment,
    )


T = TypeVar("T", bound="ResponseCreatePaymentConsentData")


@_attrs_define
class ResponseCreatePaymentConsentData:
    """Objeto contendo as informações de consentimento para a iniciação de pagamento.

    Attributes:
        consent_id (str): Identificador único do consentimento criado para a iniciação de pagamento solicitada. Deverá
            ser um URN - Uniform Resource Name.
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
             Example: urn:bancoex:C1DD33123.
        creation_date_time (datetime.datetime): Data e hora em que o consentimento foi criado. Uma string com data e
            hora conforme especificação RFC-3339, sempre com a utilização de timezone UTC(UTC time format). Example:
            2021-05-21T08:30:00Z.
        expiration_date_time (datetime.datetime): Data e hora em que o consentimento da iniciação de pagamento expira.
            Para consentimentos em status AWAITING_AUTHORISATION, deve ser sempre “creationDateTime + 5 minutos”.
            Após esse tempo, não sendo aprovado (seja a aprovação única ou primeiro aprovador), o consentimento deve ir para
            REJECTED.
            Para consentimentos em status PARTIALLY_ACCEPTED, deve assumir o valor da política de aprovação de cada
            instituição.
            Para consentimentos em status AUTHORISED, devem assumir o valor de “statusUpdateDateTime + 60 minutos”, sendo
            esse o tempo máximo permitido para o consumo do consentimento.
            Caso não seja consumido, deve ser movido para o status REJECTED.
             Example: 2021-05-21T08:30:00Z.
        status_update_date_time (datetime.datetime): Data e hora em que o recurso foi atualizado. Uma string com data e
            hora conforme especificação RFC-3339, sempre com a utilização de timezone UTC(UTC time format).
             Example: 2021-05-21T08:30:00Z.
        status (EnumAuthorisationStatusType): Retorna o estado do consentimento, o qual no momento de sua criação será
            AWAITING_AUTHORISATION. Na situação de múltiplas alçadas PARTIALLY_ACCEPTED, indica que consentimento precisa da
            confirmação de mais autorizadores. Este estado será alterado depois da(s) autorização(ões) do(s)
            consentimento(s) na detentora da conta do pagador (Debtor) para AUTHORISED ou REJECTED. O consentimento fica no
            estado CONSUMED após ocorrer a iniciação do pagamento referente ao consentimento.

            Em caso de consentimento expirado a detentora deverá retornar o status REJECTED.


            Estados possíveis:

            AWAITING_AUTHORISATION - Aguardando autorização

            PARTIALLY_ACCEPTED – Aguardando múltiplas alçadas

            AUTHORISED - Autorizado

            REJECTED - Rejeitado

            CONSUMED - Consumido
             Example: AWAITING_AUTHORISATION.
        logged_user (LoggedUser): Usuário (pessoa natural) que encontra-se logado na instituição Iniciadora de
            Pagamento.
        creditor (Identification): Objeto contendo os dados do recebedor (creditor).
        payment (ResponseCreatePaymentConsentDataPayment): Objeto contendo dados de pagamento para consentimento.
        business_entity (BusinessEntity | Unset): Usuário (pessoa jurídica) que encontra-se logado na instituição
            Iniciadora de Pagamento. [Restrição] Preenchimento obrigatório se usuário logado na instituição Iniciadora de
            Pagamento for um CNPJ (pessoa jurídica).
        debtor_account (ConsentsDebtorAccount | Unset): Objeto que contém a identificação da conta de origem do pagador.
            As informações quanto à conta de origem do pagador poderão ser trazidas no consentimento para a detentora, caso
            a iniciadora tenha coletado essas informações do cliente.
            No caso em que o cliente não preenche os dados na iniciadora, a detentora deverá persistir as informações da
            conta selecionada seguindo as condições abaixo.

            [Restrição]
            - AUTHORISED e CONSUMED: Para esses dois status, o preenchimento do campo deverá ser obrigatório.
            - REJECTED: Para este status o preenchimento é condicional, dado que há cenários em que a detentora também não
            terá conhecimento da conta origem, pois a mesma não foi selecionada pelo usuário. Nos casos em que houver
            seleção, a conta deve ser preenchida obrigatoriamente.
    """

    consent_id: str
    creation_date_time: datetime.datetime
    expiration_date_time: datetime.datetime
    status_update_date_time: datetime.datetime
    status: EnumAuthorisationStatusType
    logged_user: 'LoggedUser'
    creditor: 'Identification'
    payment: 'ResponseCreatePaymentConsentDataPayment'
    business_entity: 'BusinessEntity | Unset' = UNSET
    debtor_account: 'ConsentsDebtorAccount | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        consent_id = self.consent_id

        creation_date_time = self.creation_date_time.isoformat()

        expiration_date_time = self.expiration_date_time.isoformat()

        status_update_date_time = self.status_update_date_time.isoformat()

        status = self.status.value

        logged_user = self.logged_user.to_dict()

        creditor = self.creditor.to_dict()

        payment = self.payment.to_dict()

        business_entity: dict[str, Any] | Unset = UNSET
        if not isinstance(self.business_entity, Unset):
            business_entity = self.business_entity.to_dict()

        debtor_account: dict[str, Any] | Unset = UNSET
        if not isinstance(self.debtor_account, Unset):
            debtor_account = self.debtor_account.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "consentId": consent_id,
                "creationDateTime": creation_date_time,
                "expirationDateTime": expiration_date_time,
                "statusUpdateDateTime": status_update_date_time,
                "status": status,
                "loggedUser": logged_user,
                "creditor": creditor,
                "payment": payment,
            }
        )
        if business_entity is not UNSET:
            field_dict["businessEntity"] = business_entity
        if debtor_account is not UNSET:
            field_dict["debtorAccount"] = debtor_account

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.business_entity import BusinessEntity
        from clients.payments_v4_0_0.models.consents_debtor_account import ConsentsDebtorAccount
        from clients.payments_v4_0_0.models.identification import Identification
        from clients.payments_v4_0_0.models.logged_user import LoggedUser
        from clients.payments_v4_0_0.models.response_create_payment_consent_data_payment import (
            ResponseCreatePaymentConsentDataPayment,
        )

        d = dict(src_dict)
        consent_id = d.pop("consentId")

        creation_date_time = isoparse(d.pop("creationDateTime"))

        expiration_date_time = isoparse(d.pop("expirationDateTime"))

        status_update_date_time = isoparse(d.pop("statusUpdateDateTime"))

        status = EnumAuthorisationStatusType(d.pop("status"))

        logged_user = LoggedUser.from_dict(d.pop("loggedUser"))

        creditor = Identification.from_dict(d.pop("creditor"))

        payment = ResponseCreatePaymentConsentDataPayment.from_dict(d.pop("payment"))

        _business_entity = d.pop("businessEntity", UNSET)
        business_entity: 'BusinessEntity | Unset'
        if isinstance(_business_entity, Unset):
            business_entity = UNSET
        else:
            business_entity = BusinessEntity.from_dict(_business_entity)

        _debtor_account = d.pop("debtorAccount", UNSET)
        debtor_account: 'ConsentsDebtorAccount | Unset'
        if isinstance(_debtor_account, Unset):
            debtor_account = UNSET
        else:
            debtor_account = ConsentsDebtorAccount.from_dict(_debtor_account)

        response_create_payment_consent_data = cls(
            consent_id=consent_id,
            creation_date_time=creation_date_time,
            expiration_date_time=expiration_date_time,
            status_update_date_time=status_update_date_time,
            status=status,
            logged_user=logged_user,
            creditor=creditor,
            payment=payment,
            business_entity=business_entity,
            debtor_account=debtor_account,
        )

        response_create_payment_consent_data.additional_properties = d
        return response_create_payment_consent_data

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
