"""Field422ResponseErrorCreatePixPaymentsErrorsItem: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_errors_create_payment import EnumErrorsCreatePayment

T = TypeVar("T", bound="Field422ResponseErrorCreatePixPaymentsErrorsItem")


@_attrs_define
class Field422ResponseErrorCreatePixPaymentsErrorsItem:
    """
    Attributes:
        code (EnumErrorsCreatePayment): Códigos de erros previstos na criação da iniciação de pagamento:
            - SALDO_INSUFICIENTE: Esta conta não possui saldo suficiente para realizar o pagamento.
            - VALOR_ACIMA_LIMITE: O valor (ou quantidade de transações) ultrapassa a faixa de limite parametrizada na
            detentora para permitir a realização de transações pelo cliente.
            - VALOR_INVALIDO: O valor enviado não é válido para o QR Code informado.
            - COBRANCA_INVALIDA: Validação de expiração, validação de vencimento, Status Válido.
            - CONSENTIMENTO_INVALIDO – Consentimento inválido (em status final).
            - PARAMETRO_NAO_INFORMADO: Parâmetro não informado.
            - PARAMETRO_INVALIDO: Parâmetro inválido.
            - NAO_INFORMADO: Não informada pela detentora de conta.
            - PAGAMENTO_DIVERGENTE_CONSENTIMENTO: Dados do pagamento divergentes dos dados do consentimento.
            - DETALHE_PAGAMENTO_INVALIDO: Detalhe do pagamento inválido.
            - PAGAMENTO_RECUSADO_DETENTORA: Pagamento recusado pela detentora de conta.
            - PAGAMENTO_RECUSADO_SPI: Pagamento recusado no Sistema de Pagamentos Instantâneos (SPI).
            - ERRO_IDEMPOTENCIA: Erro idempotência.
            - CONSENTIMENTO_PENDENTE_AUTORIZACAO: Consentimento pendente autorização de múltiplas alçadas (status
            “PARTIALLY_ACCEPTED”)
             Example: SALDO_INSUFICIENTE.
        title (str): Título específico do erro reportado, de acordo com o código enviado:
            - SALDO_INSUFICIENTE: Saldo insuficiente.
            - VALOR_ACIMA_LIMITE: Acima do limite estabelecido.
            - VALOR_INVALIDO: Valor inválido.
            - COBRANCA_INVALIDA: Cobrança inválida.
            - CONSENTIMENTO_INVALIDO – Consentimento inválido (em status final).
            - PARAMETRO_NAO_INFORMADO: Parâmetro obrigatório não informado.
            - PARAMETRO_INVALIDO: Parâmetro com valor inválido.
            - NAO_INFORMADO: Não informado.
            - PAGAMENTO_DIVERGENTE_CONSENTIMENTO: Divergência entre pagamento e consentimento.
            - DETALHE_PAGAMENTO_INVALIDO: Detalhe do pagamento inválido.
            - PAGAMENTO_RECUSADO_DETENTORA: Pagamento recusado pela detentora de conta.
            - PAGAMENTO_RECUSADO_SPI: Pagamento recusado no Sistema de Pagamentos Instantâneos (SPI).
            - ERRO_IDEMPOTENCIA: Erro idempotência.
            - CONSENTIMENTO_PENDENTE_AUTORIZACAO: Consentimento pendente autorização de múltiplas alçadas (status
            “PARTIALLY_ACCEPTED”).
             Example: Saldo insuficiente..
        detail (str): Descrição específica do erro de acordo com o código reportado:
            - SALDO_INSUFICIENTE: A conta selecionada não possui saldo suficiente para realizar o pagamento.
            - VALOR_ACIMA_LIMITE: O valor (ou quantidade de transações) ultrapassa a faixa de limite parametrizada na
            detentora para permitir a realização de transações pelo cliente.
            - VALOR_INVALIDO: O valor enviado não é válido para o QR Code informado.
            - COBRANCA_INVALIDA: Validação de expiração, validação de vencimento ou Status Válido.
            - CONSENTIMENTO_INVALIDO – Consentimento inválido (em status final).
            - PARAMETRO_NAO_INFORMADO: endToEndId
            - PARAMETRO_INVALIDO: endToEndId
            - NAO_INFORMADO: Não reportado/identificado pela instituição detentora de conta.
            - PAGAMENTO_DIVERGENTE_CONSENTIMENTO: Dados do pagamento divergentes dos dados do consentimento.
            - DETALHE_PAGAMENTO_INVALIDO: Parâmetro [nome_campo] não obedece às regras de negócio.
            - PAGAMENTO_RECUSADO_DETENTORA: [descrição do motivo de recusa].
            - PAGAMENTO_RECUSADO_SPI: [código de erro conforme tabela de domínios reason PACS.002].
            - ERRO_IDEMPOTENCIA: Conteúdo da mensagem (claim data) diverge do conteúdo associado a esta chave de
            idempotência (x-idempotency-key).
            - CONSENTIMENTO_PENDENTE_AUTORIZACAO: Consentimento pendente autorização de múltiplas alçadas (status
            “PARTIALLY_ACCEPTED”).
             Example: A conta selecionada não possui saldo suficiente para realizar o pagamento..
    """

    code: EnumErrorsCreatePayment
    title: str
    detail: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code.value

        title = self.title

        detail = self.detail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "title": title,
                "detail": detail,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = EnumErrorsCreatePayment(d.pop("code"))

        title = d.pop("title")

        detail = d.pop("detail")

        field_422_response_error_create_pix_payments_errors_item = cls(
            code=code,
            title=title,
            detail=detail,
        )

        field_422_response_error_create_pix_payments_errors_item.additional_properties = d
        return field_422_response_error_create_pix_payments_errors_item

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
