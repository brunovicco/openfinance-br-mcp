"""ConsentsGetConsentsConsentIdResponse529ErrorsItem: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ConsentsGetConsentsConsentIdResponse529ErrorsItem")


@_attrs_define
class ConsentsGetConsentsConsentIdResponse529ErrorsItem:
    """
    Attributes:
        code (str): Código de erro específico do endpoint
        title (str): Título legível por humanos deste erro específico
        detail (str): Descrição legível por humanos deste erro específico
    """

    code: str
    title: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        title = self.title

        detail = self.detail

        field_dict: dict[str, Any] = {}

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
        code = d.pop("code")

        title = d.pop("title")

        detail = d.pop("detail")

        consents_get_consents_consent_id_response_529_errors_item = cls(
            code=code,
            title=title,
            detail=detail,
        )

        return consents_get_consents_consent_id_response_529_errors_item
