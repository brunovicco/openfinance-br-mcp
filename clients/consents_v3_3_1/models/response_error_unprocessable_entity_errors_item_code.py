"""ResponseErrorUnprocessableEntityErrorsItemCode: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from enum import Enum


class ResponseErrorUnprocessableEntityErrorsItemCode(str, Enum):
    COMBINACAO_PERMISSOES_INCORRETA = "COMBINACAO_PERMISSOES_INCORRETA"
    DATA_EXPIRACAO_INVALIDA = "DATA_EXPIRACAO_INVALIDA"
    ERRO_NAO_MAPEADO = "ERRO_NAO_MAPEADO"
    INFORMACOES_PJ_NAO_INFORMADAS = "INFORMACOES_PJ_NAO_INFORMADAS"
    PERMISSAO_PF_PJ_EM_CONJUNTO = "PERMISSAO_PF_PJ_EM_CONJUNTO"
    PERMISSOES_PJ_INCORRETAS = "PERMISSOES_PJ_INCORRETAS"
    SEM_PERMISSOES_FUNCIONAIS_RESTANTES = "SEM_PERMISSOES_FUNCIONAIS_RESTANTES"

    def __str__(self) -> str:
        return str(self.value)
