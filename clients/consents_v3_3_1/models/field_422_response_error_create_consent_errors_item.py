"""Field422ResponseErrorCreateConsentErrorsItem: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.consents_v3_3_1.models.field_422_response_error_create_consent_errors_item_code import (
    Field422ResponseErrorCreateConsentErrorsItemCode,
)

T = TypeVar("T", bound="Field422ResponseErrorCreateConsentErrorsItem")


@_attrs_define
class Field422ResponseErrorCreateConsentErrorsItem:
    """
    Attributes:
        code (Field422ResponseErrorCreateConsentErrorsItemCode): Códigos de erros previstos na durante o processo de
            extensão do consentimento:
             - DEPENDE_MULTIPLA_ALCADA: Necessário aprovação de múltipla alçada.
             - ESTADO_CONSENTIMENTO_INVALIDO: Estado inválido do consentimento.
             - DATA_EXPIRACAO_INVALIDA: Nova data para expiração do consentimento é inválida.
             - ERRO_NAO_MAPEADO: Utilizado quando não houver um code de erro definido.
             Example: DEPENDE_MULTIPLA_ALCADA.
        title (str): Título específico do erro reportado, de acordo com o código enviado:
            - DEPENDE_MULTIPLA_ALCADA: Necessário aprovação de múltipla alçada.
            - ESTADO_CONSENTIMENTO_INVALIDO: Estado inválido do consentimento.
            - DATA_EXPIRACAO_INVALIDA: Nova data para expiração do consentimento é inválida.
            - ERRO_NAO_MAPEADO: Utilizado quando não houver um code de erro definido. O texto deve deixar claro o motivo do
            erro ocorrido.
             Example: Necessário aprovação de múltipla alçada..
        detail (str): Título específico do erro reportado, de acordo com o código enviado:
            - DEPENDE_MULTIPLA_ALCADA: O consentimento informado não pode ser renovado sem redirecionamento porque depende
            de múltipla alçada para aprovação.
            - ESTADO_CONSENTIMENTO_INVALIDO: O consentimento informado não pode ser renovado sem redirecionamento porque
            está em um estado que não permite a renovação.
            - DATA_EXPIRACAO_INVALIDA: O consentimento informado não pode ser renovado pois a nova data de expiração não
            segue a convenção do ecossistema.
            - ERRO_NAO_MAPEADO: Utilizado quando não houver um code de erro definido. O texto deve deixar claro o motivo do
            erro ocorrido.
             Example: O consentimento informado não pode ser renovado sem redirecionamento porque depende de múltipla alçada
            para aprovação..
    """

    code: Field422ResponseErrorCreateConsentErrorsItemCode
    title: str
    detail: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code.value

        title = self.title

        detail = self.detail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "title": title,
                "detail": detail,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = Field422ResponseErrorCreateConsentErrorsItemCode(d.pop("code"))

        title = d.pop("title")

        detail = d.pop("detail")

        field_422_response_error_create_consent_errors_item = cls(
            code=code,
            title=title,
            detail=detail,
        )

        field_422_response_error_create_consent_errors_item.additional_properties = d
        return field_422_response_error_create_consent_errors_item

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
