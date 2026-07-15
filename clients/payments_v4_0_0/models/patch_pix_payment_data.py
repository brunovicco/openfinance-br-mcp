"""PatchPixPaymentData: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_payment_cancellation_status_type import (
    EnumPaymentCancellationStatusType,
)

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.patch_pix_payment_data_cancellation import (
        PatchPixPaymentDataCancellation,
    )


T = TypeVar("T", bound="PatchPixPaymentData")


@_attrs_define
class PatchPixPaymentData:
    """
    Attributes:
        status (EnumPaymentCancellationStatusType): Utilizado para informar para qual estado deve ir o pagamento.
            Atualmente o único valor possível é CANC.
             Example: CANC.
        cancellation (PatchPixPaymentDataCancellation): Objeto que agrupa as informações de qual foi o usuário pagador
            que solicitou o cancelamento da transação.
            Observação: este campo é necessário porque, em casos de múltiplas alçadas de autorização, é possível que o
            pagamento seja solicitado por um usuário pagador e cancelado por outro.
    """

    status: EnumPaymentCancellationStatusType
    cancellation: 'PatchPixPaymentDataCancellation'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        cancellation = self.cancellation.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "cancellation": cancellation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.patch_pix_payment_data_cancellation import (
            PatchPixPaymentDataCancellation,
        )

        d = dict(src_dict)
        status = EnumPaymentCancellationStatusType(d.pop("status"))

        cancellation = PatchPixPaymentDataCancellation.from_dict(d.pop("cancellation"))

        patch_pix_payment_data = cls(
            status=status,
            cancellation=cancellation,
        )

        patch_pix_payment_data.additional_properties = d
        return patch_pix_payment_data

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
