"""Field422ResponseErrorCreatePixPaymentErrorsItem: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_errors_create_pix_payment import EnumErrorsCreatePixPayment

T = TypeVar("T", bound="Field422ResponseErrorCreatePixPaymentErrorsItem")


@_attrs_define
class Field422ResponseErrorCreatePixPaymentErrorsItem:
    """
    Attributes:
        code (EnumErrorsCreatePixPayment): Códigos de erros previstos na criação da iniciação de pagamento:

            • PAGAMENTO_NAO_PERMITE_CANCELAMENTO: Pagamento não permite cancelamento
             Example: PAGAMENTO_NAO_PERMITE_CANCELAMENTO.
        title (str): Título específico do erro reportado, de acordo com o código enviado:

            • PAGAMENTO_NAO_PERMITE_CANCELAMENTO: Pagamento não permite cancelamento
             Example: Pagamento não permite cancelamento..
        detail (str): Descrição específica do erro de acordo com o código reportado:

            • PAGAMENTO_NAO_PERMITE_CANCELAMENTO: Pagamento não permite cancelamento
             Example: Pagamento não permite cancelamento..
    """

    code: EnumErrorsCreatePixPayment
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
        code = EnumErrorsCreatePixPayment(d.pop("code"))

        title = d.pop("title")

        detail = d.pop("detail")

        field_422_response_error_create_pix_payment_errors_item = cls(
            code=code,
            title=title,
            detail=detail,
        )

        field_422_response_error_create_pix_payment_errors_item.additional_properties = d
        return field_422_response_error_create_pix_payment_errors_item

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
