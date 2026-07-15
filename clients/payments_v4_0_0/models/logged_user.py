"""Payments API model: Usuário (pessoa natural) que encontra-se logado na instituição Iniciadora de Pagamento."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.logged_user_document import LoggedUserDocument


T = TypeVar("T", bound="LoggedUser")


@_attrs_define
class LoggedUser:
    """Usuário (pessoa natural) que encontra-se logado na instituição Iniciadora de Pagamento.

    Attributes:
        document (LoggedUserDocument):
    """

    document: 'LoggedUserDocument'
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
        from clients.payments_v4_0_0.models.logged_user_document import LoggedUserDocument

        d = dict(src_dict)
        document = LoggedUserDocument.from_dict(d.pop("document"))

        logged_user = cls(
            document=document,
        )

        logged_user.additional_properties = d
        return logged_user

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
