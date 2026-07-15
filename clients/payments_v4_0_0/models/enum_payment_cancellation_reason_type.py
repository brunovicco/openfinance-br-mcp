"""EnumPaymentCancellationReasonType: enum of possible values (CANCELADO_AGENDAMENTO, CANCELADO_MULTIPLAS_ALCADAS, CANCELADO_PENDENCIA) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumPaymentCancellationReasonType(str, Enum):
    CANCELADO_AGENDAMENTO = "CANCELADO_AGENDAMENTO"
    CANCELADO_MULTIPLAS_ALCADAS = "CANCELADO_MULTIPLAS_ALCADAS"
    CANCELADO_PENDENCIA = "CANCELADO_PENDENCIA"

    def __str__(self) -> str:
        return str(self.value)
