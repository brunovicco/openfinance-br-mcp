"""ResponseErrorUnprocessableEntityErrorsItem: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.consents_v3_3_1.models.response_error_unprocessable_entity_errors_item_code import (
    ResponseErrorUnprocessableEntityErrorsItemCode,
)

T = TypeVar("T", bound="ResponseErrorUnprocessableEntityErrorsItem")


@_attrs_define
class ResponseErrorUnprocessableEntityErrorsItem:
    """
    Attributes:
        code (ResponseErrorUnprocessableEntityErrorsItemCode): - SEM_PERMISSOES_FUNCIONAIS_RESTANTES
            - INFORMACOES_PJ_NAO_INFORMADAS
            - PERMISSOES_PJ_INCORRETAS
            - PERMISSAO_PF_PJ_EM_CONJUNTO
            - COMBINACAO_PERMISSOES_INCORRETA
            - DATA_EXPIRACAO_INVALIDA
            - ERRO_NAO_MAPEADO

            A opção “ERRO_NAO_MAPEADO” só deve ser utilizada caso não haja um code especifico mapeado para o erro.
             Example: SEM_PERMISSOES_FUNCIONAIS_RESTANTES.
        title (str): Título legível por humanos deste erro específico.
        detail (str): Descrição legível por humanos deste erro específico.
    """

    code: ResponseErrorUnprocessableEntityErrorsItemCode
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
        code = ResponseErrorUnprocessableEntityErrorsItemCode(d.pop("code"))

        title = d.pop("title")

        detail = d.pop("detail")

        response_error_unprocessable_entity_errors_item = cls(
            code=code,
            title=title,
            detail=detail,
        )

        response_error_unprocessable_entity_errors_item.additional_properties = d
        return response_error_unprocessable_entity_errors_item

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
