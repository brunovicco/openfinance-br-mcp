"""Payments API model: Objeto que consolida os dados do documento do usuário que solicitou o cancelamento."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PatchPixPaymentCancellationCancelledByDocument")


@_attrs_define
class PatchPixPaymentCancellationCancelledByDocument:
    """Objeto que consolida os dados do documento do usuário que solicitou o cancelamento.

    Attributes:
        identification (str): Número do documento do usuário pagador responsável pelo cancelamento do pagamento.
            Example: 11111111111.
        rel (str): Tipo do documento do usuário pagador responsável pelo cancelamento do pagamento. Example: CPF.
    """

    identification: str
    rel: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identification = self.identification

        rel = self.rel

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identification": identification,
                "rel": rel,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identification = d.pop("identification")

        rel = d.pop("rel")

        patch_pix_payment_cancellation_cancelled_by_document = cls(
            identification=identification,
            rel=rel,
        )

        patch_pix_payment_cancellation_cancelled_by_document.additional_properties = d
        return patch_pix_payment_cancellation_cancelled_by_document

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
