"""EnumCreditCardAccountFee: enum of possible values (ANUIDADE, AVALIACAO_EMERGENCIAL_CREDITO, EMISSAO_SEGUNDA_VIA, OUTRA, SAQUE_CARTAO_BRASIL, SAQUE_CARTAO_EXTERIOR, ...) for this field, per the Credit Cards Accounts OpenAPI spec."""

from enum import Enum


class EnumCreditCardAccountFee(str, Enum):
    ANUIDADE = "ANUIDADE"
    AVALIACAO_EMERGENCIAL_CREDITO = "AVALIACAO_EMERGENCIAL_CREDITO"
    EMISSAO_SEGUNDA_VIA = "EMISSAO_SEGUNDA_VIA"
    OUTRA = "OUTRA"
    SAQUE_CARTAO_BRASIL = "SAQUE_CARTAO_BRASIL"
    SAQUE_CARTAO_EXTERIOR = "SAQUE_CARTAO_EXTERIOR"
    SMS = "SMS"
    TARIFA_PAGAMENTO_CONTAS = "TARIFA_PAGAMENTO_CONTAS"

    def __str__(self) -> str:
        return str(self.value)
