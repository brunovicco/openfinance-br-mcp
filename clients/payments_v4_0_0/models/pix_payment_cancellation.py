"""Payments API model: Objeto que contém os dados referentes ao usuário pagador que solicitou o cancelamento, o canal utilizado por ele e o"""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.payments_v4_0_0.models.enum_payment_cancellation_from_type import EnumPaymentCancellationFromType
from clients.payments_v4_0_0.models.enum_payment_cancellation_reason_type import (
    EnumPaymentCancellationReasonType,
)

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.pix_payment_cancellation_cancelled_by import (
        PixPaymentCancellationCancelledBy,
    )


T = TypeVar("T", bound="PixPaymentCancellation")


@_attrs_define
class PixPaymentCancellation:
    """Objeto que contém os dados referentes ao usuário pagador que solicitou o cancelamento, o canal utilizado por ele e o
    motivo.

    [Restrição] O objeto cancellation será obrigatório apenas quando o valor do campo status for igual a CANC.

        Attributes:
            reason (EnumPaymentCancellationReasonType): O preenchimento desse campo para retorno, deve ocorrer pela
                detentora de contas a partir do status em que o pagamento estiver no momento da solicitação do cancelamento (ex.
                Status de pagamento = PDNG, campo deve ser preenchido com enum CANCELADO_PENDENCIA)

                Valores possíveis:

                CANCELADO_PENDENCIA - Pagamento cancelado enquanto estava na situação PDNG

                CANCELADO_AGENDAMENTO - Pagamento cancelado enquanto estava na situação SCHD

                CANCELADO_MULTIPLAS_ALCADAS - Pagamento cancelado enquanto estava na situação PATC
                 Example: CANCELADO_PENDENCIA.
            cancelled_from (EnumPaymentCancellationFromType): Campo utilizado para informar o meio pelo qual foi realizado o
                cancelamento.

                Valores possíveis:

                INICIADORA - Pagamento cancelado pelo usuário pagador nos canais da iniciadora

                DETENTORA - Pagamento cancelado pelo usuário pagador nos canais da detentora
                 Example: INICIADORA.
            cancelled_at (datetime.datetime): Data e hora que foi realizado o cancelamento, conforme especificação RFC-3339,
                formato UTC. Example: 2021-05-21T08:30:00Z.
            cancelled_by (PixPaymentCancellationCancelledBy): Informação relacionada ao usuário pagador que solicitou o
                cancelamento do pagamento.
    """

    reason: EnumPaymentCancellationReasonType
    cancelled_from: EnumPaymentCancellationFromType
    cancelled_at: datetime.datetime
    cancelled_by: 'PixPaymentCancellationCancelledBy'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason = self.reason.value

        cancelled_from = self.cancelled_from.value

        cancelled_at = self.cancelled_at.isoformat()

        cancelled_by = self.cancelled_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reason": reason,
                "cancelledFrom": cancelled_from,
                "cancelledAt": cancelled_at,
                "cancelledBy": cancelled_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.pix_payment_cancellation_cancelled_by import (
            PixPaymentCancellationCancelledBy,
        )

        d = dict(src_dict)
        reason = EnumPaymentCancellationReasonType(d.pop("reason"))

        cancelled_from = EnumPaymentCancellationFromType(d.pop("cancelledFrom"))

        cancelled_at = isoparse(d.pop("cancelledAt"))

        cancelled_by = PixPaymentCancellationCancelledBy.from_dict(d.pop("cancelledBy"))

        pix_payment_cancellation = cls(
            reason=reason,
            cancelled_from=cancelled_from,
            cancelled_at=cancelled_at,
            cancelled_by=cancelled_by,
        )

        pix_payment_cancellation.additional_properties = d
        return pix_payment_cancellation

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
