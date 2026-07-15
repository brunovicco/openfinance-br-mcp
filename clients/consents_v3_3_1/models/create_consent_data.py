"""CreateConsentData: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.consents_v3_3_1.models.create_consent_data_permissions_item import (
    CreateConsentDataPermissionsItem,
)
from clients.consents_v3_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.business_entity import BusinessEntity
    from clients.consents_v3_3_1.models.logged_user import LoggedUser


T = TypeVar("T", bound="CreateConsentData")


@_attrs_define
class CreateConsentData:
    """
    Attributes:
        logged_user (LoggedUser): Usuário (pessoa natural) que encontra-se logado na instituição receptora e que
            iniciará o processo de consentimento para compartilhamento de dados.

            É obrigatório que o número do documento utilizado seja um número válido e pertencente ao usuário logado. A
            transmissora pode utilizar algoritmos de validação de documento para garantir que se trata de um documento
            válido, como por exemplo: Cálculo de DV módulo 11 para o CPF.
        permissions (list[CreateConsentDataPermissionsItem]):  Example: ['ACCOUNTS_READ',
            'ACCOUNTS_OVERDRAFT_LIMITS_READ', 'RESOURCES_READ'].
        business_entity (BusinessEntity | Unset): Titular, pessoa jurídica a quem se referem os dados que são objeto de
            compartilhamento.

            É obrigatório que o número do CNPJ utilizado seja um número válido. A transmissora pode utilizar algoritmos de
            validação de documento para garantir que se trata de um documento válido, como por exemplo: Cálculo de DV módulo
            11 para o CNPJ.
        expiration_date_time (datetime.datetime | Unset): Data e hora de expiração da permissão. Reflete a data limite
            de validade do consentimento.
            Uma string com data e hora conforme especificação RFC-3339, sempre com a utilização de timezone UTC (UTC time
            format).

            [Restrição] De preenchimento obrigatório nos casos em que houver validade determinada.
            Em casos de consentimento com prazo indeterminado o campo não deve ser enviado.
             Example: 2021-05-21T08:30:00Z.
        is_linked (bool | Unset): Campo para identificação de consentimento iniciado em Jornada Otimizada. [RESTRIÇÃO]
            Campo de preenchimento obrigatório para todo consentimento iniciado a partir da jornada otimizada, independente
            do status do consentimento.
             Example: True.
    """

    logged_user: 'LoggedUser'
    permissions: list[CreateConsentDataPermissionsItem]
    business_entity: 'BusinessEntity | Unset' = UNSET
    expiration_date_time: datetime.datetime | Unset = UNSET
    is_linked: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logged_user = self.logged_user.to_dict()

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        business_entity: dict[str, Any] | Unset = UNSET
        if not isinstance(self.business_entity, Unset):
            business_entity = self.business_entity.to_dict()

        expiration_date_time: str | Unset = UNSET
        if not isinstance(self.expiration_date_time, Unset):
            expiration_date_time = self.expiration_date_time.isoformat()

        is_linked = self.is_linked

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "loggedUser": logged_user,
                "permissions": permissions,
            }
        )
        if business_entity is not UNSET:
            field_dict["businessEntity"] = business_entity
        if expiration_date_time is not UNSET:
            field_dict["expirationDateTime"] = expiration_date_time
        if is_linked is not UNSET:
            field_dict["isLinked"] = is_linked

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.business_entity import BusinessEntity
        from clients.consents_v3_3_1.models.logged_user import LoggedUser

        d = dict(src_dict)
        logged_user = LoggedUser.from_dict(d.pop("loggedUser"))

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = CreateConsentDataPermissionsItem(permissions_item_data)

            permissions.append(permissions_item)

        _business_entity = d.pop("businessEntity", UNSET)
        business_entity: 'BusinessEntity | Unset'
        if isinstance(_business_entity, Unset):
            business_entity = UNSET
        else:
            business_entity = BusinessEntity.from_dict(_business_entity)

        _expiration_date_time = d.pop("expirationDateTime", UNSET)
        expiration_date_time: datetime.datetime | Unset
        if isinstance(_expiration_date_time, Unset):
            expiration_date_time = UNSET
        else:
            expiration_date_time = isoparse(_expiration_date_time)

        is_linked = d.pop("isLinked", UNSET)

        create_consent_data = cls(
            logged_user=logged_user,
            permissions=permissions,
            business_entity=business_entity,
            expiration_date_time=expiration_date_time,
            is_linked=is_linked,
        )

        create_consent_data.additional_properties = d
        return create_consent_data

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
