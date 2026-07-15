"""Payments API model: Informação relacionada ao usuário pagador que solicitou o cancelamento do pagamento."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.patch_pix_payment_cancellation_cancelled_by_document import (
        PatchPixPaymentCancellationCancelledByDocument,
    )


T = TypeVar("T", bound="PatchPixPaymentCancellationCancelledBy")


@_attrs_define
class PatchPixPaymentCancellationCancelledBy:
    """Informação relacionada ao usuário pagador que solicitou o cancelamento do pagamento.

    Attributes:
        document (PatchPixPaymentCancellationCancelledByDocument): Objeto que consolida os dados do documento do usuário
            que solicitou o cancelamento.
    """

    document: 'PatchPixPaymentCancellationCancelledByDocument'
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
        from clients.payments_v4_0_0.models.patch_pix_payment_cancellation_cancelled_by_document import (
            PatchPixPaymentCancellationCancelledByDocument,
        )

        d = dict(src_dict)
        document = PatchPixPaymentCancellationCancelledByDocument.from_dict(
            d.pop("document")
        )

        patch_pix_payment_cancellation_cancelled_by = cls(
            document=document,
        )

        patch_pix_payment_cancellation_cancelled_by.additional_properties = d
        return patch_pix_payment_cancellation_cancelled_by

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
