"""Payments API model: Motivo da rejeição do consentimento. Informações complementares sobre o motivo do status."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_consent_rejection_reason_type import EnumConsentRejectionReasonType

T = TypeVar("T", bound="ConsentRejectionReason")


@_attrs_define
class ConsentRejectionReason:
    """Motivo da rejeição do consentimento. Informações complementares sobre o motivo do status.

    [Restrição] Esse motivo deverá ser enviado quando o campo /data/status for igual a REJECTED.

        Attributes:
            code (EnumConsentRejectionReasonType): Define o código da razão pela qual o consentimento foi rejeitado
                - VALOR_INVALIDO
                - NAO_INFORMADO
                - FALHA_INFRAESTRUTURA
                - TEMPO_EXPIRADO_AUTORIZACAO
                - TEMPO_EXPIRADO_CONSUMO
                - REJEITADO_USUARIO
                - CONTAS_ORIGEM_DESTINO_IGUAIS
                - CONTA_NAO_PERMITE_PAGAMENTO
                - SALDO_INSUFICIENTE
                - VALOR_ACIMA_LIMITE
                - QRCODE_INVALIDO
                 Example: SALDO_INSUFICIENTE.
            detail (str): Contém informações adicionais ao consentimento rejeitado.
                - VALOR_INVALIDO: O valor enviado não é válido para o QR Code informado;
                - NAO_INFORMADO: Não informada pela detentora de conta;
                - FALHA_INFRAESTRUTURA: [Descrição de qual falha na infraestrutura inviabilizou o processamento].
                - TEMPO_EXPIRADO_AUTORIZACAO: Consentimento expirou antes que o usuário pudesse confirmá-lo.
                - TEMPO_EXPIRADO_CONSUMO: O usuário não finalizou o fluxo de pagamento e o consentimento expirou;
                - REJEITADO_USUARIO: O usuário rejeitou a autorização do consentimento
                - CONTAS_ORIGEM_DESTINO_IGUAIS: A conta selecionada é igual à conta destino e não permite realizar esse
                pagamento.
                - CONTA_NAO_PERMITE_PAGAMENTO: A conta selecionada é do tipo [salario/investimento/liquidação/outros] e não
                permite realizar esse pagamento.
                - SALDO_INSUFICIENTE: A conta selecionada não possui saldo suficiente para realizar o pagamento.
                - VALOR_ACIMA_LIMITE: O valor ultrapassa o limite estabelecido [na instituição/no arranjo/outro] para permitir a
                realização de transações pelo cliente.
                - QRCODE_INVALIDO: O QRCode utilizado para a iniciação de pagamento não é válido.

                [Restrição] Caso consentimento rejeitado de versões nas quais não havia o campo rejectionReason retornar o
                seguinte detail: Motivo de rejeição inexistente em versões anteriores.
                 Example: O usuário rejeitou a autorização do consentimento.
    """

    code: EnumConsentRejectionReasonType
    detail: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code.value

        detail = self.detail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "detail": detail,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = EnumConsentRejectionReasonType(d.pop("code"))

        detail = d.pop("detail")

        consent_rejection_reason = cls(
            code=code,
            detail=detail,
        )

        consent_rejection_reason.additional_properties = d
        return consent_rejection_reason

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
