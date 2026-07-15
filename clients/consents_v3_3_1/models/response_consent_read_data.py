"""ResponseConsentReadData: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.consents_v3_3_1.models.response_consent_read_data_permissions_item import (
    ResponseConsentReadDataPermissionsItem,
)
from clients.consents_v3_3_1.models.response_consent_read_data_status import ResponseConsentReadDataStatus
from clients.consents_v3_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.response_consent_read_data_journey import (
        ResponseConsentReadDataJourney,
    )
    from clients.consents_v3_3_1.models.response_consent_read_data_rejection import (
        ResponseConsentReadDataRejection,
    )


T = TypeVar("T", bound="ResponseConsentReadData")


@_attrs_define
class ResponseConsentReadData:
    """
    Attributes:
        consent_id (str): O consentId é o identificador único do consentimento e deverá ser um URN - Uniform Resource
            Name.
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
        creation_date_time (datetime.datetime): Data e hora em que o recurso foi criado. Uma string com data e hora
            conforme especificação RFC-3339, sempre com a utilização de timezone UTC(UTC time format). Example:
            2021-05-21T08:30:00Z.
        status (ResponseConsentReadDataStatus): Estado atual do consentimento cadastrado. Example:
            AWAITING_AUTHORISATION.
        status_update_date_time (datetime.datetime): Data e hora em que o recurso foi atualizado. Uma string com data e
            hora conforme especificação RFC-3339, sempre com a utilização de timezone UTC(UTC time format). Example:
            2021-05-21T08:30:00Z.
        permissions (list[ResponseConsentReadDataPermissionsItem]): Especifica os tipos de permissões de acesso às APIs
            no escopo do Open Finance Brasil - Dados cadastrais e transacionais, de acordo com os blocos de consentimento
            fornecidos pelo usuário e necessários ao acesso a cada endpoint das APIs. Esse array não deve ter duplicidade de
            itens. Example: ['ACCOUNTS_READ', 'ACCOUNTS_OVERDRAFT_LIMITS_READ', 'RESOURCES_READ'].
        expiration_date_time (datetime.datetime | Unset): Data e hora de expiração da permissão. Reflete a data limite
            de validade do consentimento. Uma string com data e hora conforme especificação RFC-3339, sempre com a
            utilização de timezone UTC(UTC time format).

            [Restrição] De preenchimento obrigatório nos casos em que houver validade determinada. Em casos de consentimento
            com prazo indeterminado o campo não deve ser preenchido.
             Example: 2021-05-21T08:30:00Z.
        rejection (ResponseConsentReadDataRejection | Unset): Objeto a ser retornado caso o consentimento seja
            rejeitado.
        journey (ResponseConsentReadDataJourney | Unset): Informações adicionais sobre o contexto de Jornada Otimizada.
            [RESTRIÇÃO] Objeto de envio obrigatório quando o usuário manifestar consentimento para compartilhamento de saldo
            através da Jornada Otimizada.
    """

    consent_id: str
    creation_date_time: datetime.datetime
    status: ResponseConsentReadDataStatus
    status_update_date_time: datetime.datetime
    permissions: list[ResponseConsentReadDataPermissionsItem]
    expiration_date_time: datetime.datetime | Unset = UNSET
    rejection: 'ResponseConsentReadDataRejection | Unset' = UNSET
    journey: 'ResponseConsentReadDataJourney | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        consent_id = self.consent_id

        creation_date_time = self.creation_date_time.isoformat()

        status = self.status.value

        status_update_date_time = self.status_update_date_time.isoformat()

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        expiration_date_time: str | Unset = UNSET
        if not isinstance(self.expiration_date_time, Unset):
            expiration_date_time = self.expiration_date_time.isoformat()

        rejection: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rejection, Unset):
            rejection = self.rejection.to_dict()

        journey: dict[str, Any] | Unset = UNSET
        if not isinstance(self.journey, Unset):
            journey = self.journey.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "consentId": consent_id,
                "creationDateTime": creation_date_time,
                "status": status,
                "statusUpdateDateTime": status_update_date_time,
                "permissions": permissions,
            }
        )
        if expiration_date_time is not UNSET:
            field_dict["expirationDateTime"] = expiration_date_time
        if rejection is not UNSET:
            field_dict["rejection"] = rejection
        if journey is not UNSET:
            field_dict["journey"] = journey

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.response_consent_read_data_journey import (
            ResponseConsentReadDataJourney,
        )
        from clients.consents_v3_3_1.models.response_consent_read_data_rejection import (
            ResponseConsentReadDataRejection,
        )

        d = dict(src_dict)
        consent_id = d.pop("consentId")

        creation_date_time = isoparse(d.pop("creationDateTime"))

        status = ResponseConsentReadDataStatus(d.pop("status"))

        status_update_date_time = isoparse(d.pop("statusUpdateDateTime"))

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = ResponseConsentReadDataPermissionsItem(
                permissions_item_data
            )

            permissions.append(permissions_item)

        _expiration_date_time = d.pop("expirationDateTime", UNSET)
        expiration_date_time: datetime.datetime | Unset
        if isinstance(_expiration_date_time, Unset):
            expiration_date_time = UNSET
        else:
            expiration_date_time = isoparse(_expiration_date_time)

        _rejection = d.pop("rejection", UNSET)
        rejection: 'ResponseConsentReadDataRejection | Unset'
        if isinstance(_rejection, Unset):
            rejection = UNSET
        else:
            rejection = ResponseConsentReadDataRejection.from_dict(_rejection)

        _journey = d.pop("journey", UNSET)
        journey: 'ResponseConsentReadDataJourney | Unset'
        if isinstance(_journey, Unset):
            journey = UNSET
        else:
            journey = ResponseConsentReadDataJourney.from_dict(_journey)

        response_consent_read_data = cls(
            consent_id=consent_id,
            creation_date_time=creation_date_time,
            status=status,
            status_update_date_time=status_update_date_time,
            permissions=permissions,
            expiration_date_time=expiration_date_time,
            rejection=rejection,
            journey=journey,
        )

        response_consent_read_data.additional_properties = d
        return response_consent_read_data

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
