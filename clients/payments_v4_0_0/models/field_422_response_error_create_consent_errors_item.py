"""Field422ResponseErrorCreateConsentErrorsItem: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.field_422_response_error_create_consent_errors_item_code import (
    Field422ResponseErrorCreateConsentErrorsItemCode,
)

T = TypeVar("T", bound="Field422ResponseErrorCreateConsentErrorsItem")


@_attrs_define
class Field422ResponseErrorCreateConsentErrorsItem:
    """
    Attributes:
        code (Field422ResponseErrorCreateConsentErrorsItemCode): Códigos de erros previstos na criação de consentimento
            para a iniciação de pagamentos:
            • FORMA_PAGAMENTO_INVALIDA: Forma de pagamento inválida.
            • DATA_PAGAMENTO_INVALIDA: Data de pagamento inválida.
            • DETALHE_PAGAMENTO_INVALIDO: Detalhe do pagamento inválido.
            • PARAMETRO_NAO_INFORMADO: Parâmetro não informado.
            • PARAMETRO_INVALIDO: Parâmetro inválido.
            • ERRO_IDEMPOTENCIA: Erro idempotência.
            • NAO_INFORMADO: Não informado.
             Example: FORMA_PAGAMENTO_INVALIDA.
        title (str): Título específico do erro reportado, de acordo com o código enviado:
            • FORMA_PAGAMENTO_INVALIDA: Forma de pagamento inválida.
            • DATA_PAGAMENTO_INVALIDA: Data de pagamento inválida.
            • DETALHE_PAGAMENTO_INVALIDO: Detalhe do pagamento inválido.
            • PARAMETRO_NAO_INFORMADO: Parâmetro não informado.
            • PARAMETRO_INVALIDO: Parâmetro inválido.
            • ERRO_IDEMPOTENCIA: Erro idempotência.
            • NAO_INFORMADO: Não informado.
             Example: Forma de pagamento inválida..
        detail (str): Descrição específica do erro de acordo com o código reportado:
            • FORMA_PAGAMENTO_INVALIDA: Forma de pagamento [Modalidade] não suportada.
            • DATA_PAGAMENTO_INVALIDA: Data de pagamento inválida para a forma de pagamento selecionada.
            • DETALHE_PAGAMENTO_INVALIDO: Parâmetro [nome_campo] não obedece às regras de negócio.
            • PARAMETRO_NAO_INFORMADO: Parâmetro [nome_campo] obrigatório não informado.
            • PARAMETRO_INVALIDO: Parâmetro [nome_campo] não obedece as regras de formatação esperadas.
            • ERRO_IDEMPOTENCIA: Conteúdo da mensagem (claim data) diverge do conteúdo associado a esta chave de
            idempotência (x-idempotency-key).
            • NAO_INFORMADO: Não reportado/identificado pela instituição detentora de conta.
             Example: Forma de pagamento [Modalidade] não suportada..
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
