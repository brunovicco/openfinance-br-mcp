"""CreateConsentExtensionsData: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.consents_v3_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.business_entity_extensions import BusinessEntityExtensions
    from clients.consents_v3_3_1.models.logged_user_extensions import LoggedUserExtensions


T = TypeVar("T", bound="CreateConsentExtensionsData")


@_attrs_define
class CreateConsentExtensionsData:
    """
    Attributes:
        logged_user (LoggedUserExtensions): Usuário (pessoa natural) que encontra-se logado na instituição receptora e
            que iniciará o processo de consentimento para compartilhamento de dados.
            Deve ser armazenado como novo usuário logado responsável pela renovação do consentimento atual.
        expiration_date_time (datetime.datetime | Unset): Data e hora de expiração da permissão. Reflete a data limite
            de validade do consentimento.
            Uma string com data e hora conforme especificação RFC-3339, sempre com a utilização de timezone UTC (UTC time
            format).

            [Restrição] De preenchimento obrigatório nos casos em que houver validade determinada.
            Em casos de consentimento com prazo indeterminado o campo não deve ser enviado.
             Example: 2021-05-21T08:30:00Z.
        business_entity (BusinessEntityExtensions | Unset): Titular, pessoa jurídica a quem se referem os dados que são
            objeto de compartilhamento.
            Deve ser informado apenas para casos de consentimento pessoa jurídica.
            Não precisa ser armazenado separadamente. Para fins de renovação de consentimento, será utilizado apenas para
            verificação do consentimento vigente, pois é um atributo imutável.
    """

    logged_user: 'LoggedUserExtensions'
    expiration_date_time: datetime.datetime | Unset = UNSET
    business_entity: 'BusinessEntityExtensions | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logged_user = self.logged_user.to_dict()

        expiration_date_time: str | Unset = UNSET
        if not isinstance(self.expiration_date_time, Unset):
            expiration_date_time = self.expiration_date_time.isoformat()

        business_entity: dict[str, Any] | Unset = UNSET
        if not isinstance(self.business_entity, Unset):
            business_entity = self.business_entity.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "loggedUser": logged_user,
            }
        )
        if expiration_date_time is not UNSET:
            field_dict["expirationDateTime"] = expiration_date_time
        if business_entity is not UNSET:
            field_dict["businessEntity"] = business_entity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.business_entity_extensions import BusinessEntityExtensions
        from clients.consents_v3_3_1.models.logged_user_extensions import LoggedUserExtensions

        d = dict(src_dict)
        logged_user = LoggedUserExtensions.from_dict(d.pop("loggedUser"))

        _expiration_date_time = d.pop("expirationDateTime", UNSET)
        expiration_date_time: datetime.datetime | Unset
        if isinstance(_expiration_date_time, Unset):
            expiration_date_time = UNSET
        else:
            expiration_date_time = isoparse(_expiration_date_time)

        _business_entity = d.pop("businessEntity", UNSET)
        business_entity: 'BusinessEntityExtensions | Unset'
        if isinstance(_business_entity, Unset):
            business_entity = UNSET
        else:
            business_entity = BusinessEntityExtensions.from_dict(_business_entity)

        create_consent_extensions_data = cls(
            logged_user=logged_user,
            expiration_date_time=expiration_date_time,
            business_entity=business_entity,
        )

        create_consent_extensions_data.additional_properties = d
        return create_consent_extensions_data

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
