"""EnumAccountType: enum of possible values (CONTA_DEPOSITO_A_VISTA, CONTA_PAGAMENTO_PRE_PAGA, CONTA_POUPANCA) for this field, per the Accounts OpenAPI spec."""

from enum import Enum


class EnumAccountType(str, Enum):
    CONTA_DEPOSITO_A_VISTA = "CONTA_DEPOSITO_A_VISTA"
    CONTA_PAGAMENTO_PRE_PAGA = "CONTA_PAGAMENTO_PRE_PAGA"
    CONTA_POUPANCA = "CONTA_POUPANCA"

    def __str__(self) -> str:
        return str(self.value)
