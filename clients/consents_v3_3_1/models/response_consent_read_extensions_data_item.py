"""ResponseConsentReadExtensionsDataItem: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.consents_v3_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.logged_user_extensions import LoggedUserExtensions


T = TypeVar("T", bound="ResponseConsentReadExtensionsDataItem")


@_attrs_define
class ResponseConsentReadExtensionsDataItem:
    """
    Attributes:
        logged_user (LoggedUserExtensions): Usuário (pessoa natural) que encontra-se logado na instituição receptora e
            que iniciará o processo de consentimento para compartilhamento de dados.
            Deve ser armazenado como novo usuário logado responsável pela renovação do consentimento atual.
        request_date_time (datetime.datetime): Data e hora em que o recurso foi criado. Uma string com data e hora
            conforme especificação RFC-3339, sempre com a utilização de timezone UTC(UTC time format). Example:
            2021-05-21T08:30:00Z.
        expiration_date_time (datetime.datetime | Unset): Data e hora de expiração da permissão. Reflete a data limite
            de validade do consentimento. Uma string com data e hora conforme especificação RFC-3339, sempre com a
            utilização de timezone UTC(UTC time format), utilizado apenas para consulta de alterações históricas de extensão
            do consentimento.

            [Restrição] De preenchimento obrigatório nos casos em que houver validade determinada.

            Em casos de consentimento com prazo indeterminada o campo não deve ser preenchido.
             Example: 2021-05-21T08:30:00Z.
        previous_expiration_date_time (datetime.datetime | Unset): Data e hora de expiração anteriores a renovação.
            Reflete a data limite anterior de validade do consentimento. Uma string com data e hora conforme especificação
            RFC-3339, sempre com a utilização de timezone UTC (UTC time format).

            [Restrição] De preenchimento obrigatório nos casos em que houver validade determinada. Em casos de consentimento
            com prazo indeterminado, ou renovações feitas com a v2.2.0 em que não exista persistência dessa informação, o
            campo não deve ser preenchido.
             Example: 2023-10-18T18:30:00Z.
        x_fapi_customer_ip_address (str | Unset): O endereço IP do usuário logado com o receptor que solicitou a
            renovação sem redirecionamento.

            [Restrição] De preenchimento obrigatório a partir da v3.0.0. Opcional para renovações feitas com a v2.2.0 quando
            não existir persistência dessa informação.
             Example: 172.217.22.14.
        x_customer_user_agent (str | Unset): Indica o user-agent que o usuário utilizou quando solicitou a renovação sem
            redirecionamento.

            [Restrição] De preenchimento obrigatório a partir da v3.0.0. Opcional para renovações feitas com a v2.2.0 quando
            não existir persistência dessa informação.
             Example: Mozilla/5.0 (iPhone14,6; U; CPU iPhone OS 15_4 like Mac OS X).
    """

    logged_user: 'LoggedUserExtensions'
    request_date_time: datetime.datetime
    expiration_date_time: datetime.datetime | Unset = UNSET
    previous_expiration_date_time: datetime.datetime | Unset = UNSET
    x_fapi_customer_ip_address: str | Unset = UNSET
    x_customer_user_agent: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logged_user = self.logged_user.to_dict()

        request_date_time = self.request_date_time.isoformat()

        expiration_date_time: str | Unset = UNSET
        if not isinstance(self.expiration_date_time, Unset):
            expiration_date_time = self.expiration_date_time.isoformat()

        previous_expiration_date_time: str | Unset = UNSET
        if not isinstance(self.previous_expiration_date_time, Unset):
            previous_expiration_date_time = (
                self.previous_expiration_date_time.isoformat()
            )

        x_fapi_customer_ip_address = self.x_fapi_customer_ip_address

        x_customer_user_agent = self.x_customer_user_agent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "loggedUser": logged_user,
                "requestDateTime": request_date_time,
            }
        )
        if expiration_date_time is not UNSET:
            field_dict["expirationDateTime"] = expiration_date_time
        if previous_expiration_date_time is not UNSET:
            field_dict["previousExpirationDateTime"] = previous_expiration_date_time
        if x_fapi_customer_ip_address is not UNSET:
            field_dict["xFapiCustomerIpAddress"] = x_fapi_customer_ip_address
        if x_customer_user_agent is not UNSET:
            field_dict["xCustomerUserAgent"] = x_customer_user_agent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.logged_user_extensions import LoggedUserExtensions

        d = dict(src_dict)
        logged_user = LoggedUserExtensions.from_dict(d.pop("loggedUser"))

        request_date_time = isoparse(d.pop("requestDateTime"))

        _expiration_date_time = d.pop("expirationDateTime", UNSET)
        expiration_date_time: datetime.datetime | Unset
        if isinstance(_expiration_date_time, Unset):
            expiration_date_time = UNSET
        else:
            expiration_date_time = isoparse(_expiration_date_time)

        _previous_expiration_date_time = d.pop("previousExpirationDateTime", UNSET)
        previous_expiration_date_time: datetime.datetime | Unset
        if isinstance(_previous_expiration_date_time, Unset):
            previous_expiration_date_time = UNSET
        else:
            previous_expiration_date_time = isoparse(_previous_expiration_date_time)

        x_fapi_customer_ip_address = d.pop("xFapiCustomerIpAddress", UNSET)

        x_customer_user_agent = d.pop("xCustomerUserAgent", UNSET)

        response_consent_read_extensions_data_item = cls(
            logged_user=logged_user,
            request_date_time=request_date_time,
            expiration_date_time=expiration_date_time,
            previous_expiration_date_time=previous_expiration_date_time,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_customer_user_agent=x_customer_user_agent,
        )

        response_consent_read_extensions_data_item.additional_properties = d
        return response_consent_read_extensions_data_item

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
