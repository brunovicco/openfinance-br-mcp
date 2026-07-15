"""Payments API model: Objeto que agrupa as informações de qual foi o usuário pagador que solicitou o cancelamento da transação."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.patch_pix_payment_data_cancellation_cancelled_by import (
        PatchPixPaymentDataCancellationCancelledBy,
    )


T = TypeVar("T", bound="PatchPixPaymentDataCancellation")


@_attrs_define
class PatchPixPaymentDataCancellation:
    """Objeto que agrupa as informações de qual foi o usuário pagador que solicitou o cancelamento da transação.
    Observação: este campo é necessário porque, em casos de múltiplas alçadas de autorização, é possível que o pagamento
    seja solicitado por um usuário pagador e cancelado por outro.

        Attributes:
            cancelled_by (PatchPixPaymentDataCancellationCancelledBy): Informação relacionada ao usuário pagador que
                solicitou o cancelamento do pagamento.
    """

    cancelled_by: 'PatchPixPaymentDataCancellationCancelledBy'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cancelled_by = self.cancelled_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cancelledBy": cancelled_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.patch_pix_payment_data_cancellation_cancelled_by import (
            PatchPixPaymentDataCancellationCancelledBy,
        )

        d = dict(src_dict)
        cancelled_by = PatchPixPaymentDataCancellationCancelledBy.from_dict(
            d.pop("cancelledBy")
        )

        patch_pix_payment_data_cancellation = cls(
            cancelled_by=cancelled_by,
        )

        patch_pix_payment_data_cancellation.additional_properties = d
        return patch_pix_payment_data_cancellation

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
