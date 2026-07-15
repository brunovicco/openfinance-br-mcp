"""EnumCompletedAuthorisedPaymentIndicator: enum of possible values (LANCAMENTO_FUTURO, TRANSACAO_EFETIVADA, TRANSACAO_PROCESSANDO) for this field, per the Accounts OpenAPI spec."""

from enum import Enum


class EnumCompletedAuthorisedPaymentIndicator(str, Enum):
    LANCAMENTO_FUTURO = "LANCAMENTO_FUTURO"
    TRANSACAO_EFETIVADA = "TRANSACAO_EFETIVADA"
    TRANSACAO_PROCESSANDO = "TRANSACAO_PROCESSANDO"

    def __str__(self) -> str:
        return str(self.value)
