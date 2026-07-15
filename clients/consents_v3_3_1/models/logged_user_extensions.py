"""Consents API model: Usuário (pessoa natural) que encontra-se logado na instituição receptora e que iniciará o processo de consentimento"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.logged_user_document_extensions import LoggedUserDocumentExtensions


T = TypeVar("T", bound="LoggedUserExtensions")


@_attrs_define
class LoggedUserExtensions:
    """Usuário (pessoa natural) que encontra-se logado na instituição receptora e que iniciará o processo de consentimento
    para compartilhamento de dados.
    Deve ser armazenado como novo usuário logado responsável pela renovação do consentimento atual.

        Attributes:
            document (LoggedUserDocumentExtensions):
    """

    document: 'LoggedUserDocumentExtensions'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document = self.document.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document": document,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.logged_user_document_extensions import (
            LoggedUserDocumentExtensions,
        )

        d = dict(src_dict)
        document = LoggedUserDocumentExtensions.from_dict(d.pop("document"))

        logged_user_extensions = cls(
            document=document,
        )

        logged_user_extensions.additional_properties = d
        return logged_user_extensions

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
