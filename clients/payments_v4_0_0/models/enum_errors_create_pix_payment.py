"""EnumErrorsCreatePixPayment: enum of possible values (PAGAMENTO_NAO_PERMITE_CANCELAMENTO) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumErrorsCreatePixPayment(str, Enum):
    PAGAMENTO_NAO_PERMITE_CANCELAMENTO = "PAGAMENTO_NAO_PERMITE_CANCELAMENTO"

    def __str__(self) -> str:
        return str(self.value)
