"""Payments API model: Motivo da rejeição do pagamento. Informações complementares sobre o motivo do status"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_rejection_reason_type_get_pix import EnumRejectionReasonTypeGetPix

T = TypeVar("T", bound="RejectionReasonGetPix")


@_attrs_define
class RejectionReasonGetPix:
    """Motivo da rejeição do pagamento. Informações complementares sobre o motivo do status
    [Restrição] Esse motivo deverá ser enviado quando o campo /data/status for igual a RJCT (REJECTED).

        Attributes:
            code (EnumRejectionReasonTypeGetPix): Define o código da razão pela qual o pagamento foi rejeitado

                - SALDO_INSUFICIENTE - A conta selecionada não possui saldo suficiente para realizar o pagamento.

                - VALOR_ACIMA_LIMITE - O valor ultrapassa o limite estabelecido [na instituição/no arranjo/outro] para permitir
                a realização de transações pelo cliente.

                - VALOR_INVALIDO - O valor enviado não é válido para o QR Code informado.

                - COBRANCA_INVALIDA - Validação de expiração, validação de vencimento ou Status Válido.

                - NAO_INFORMADO - Não reportado/identificado pela instituição detentora de conta.

                - PAGAMENTO_DIVERGENTE_CONSENTIMENTO - Dados do pagamento divergentes dos dados do consentimento.

                - DETALHE_PAGAMENTO_INVALIDO - Parâmetro [nome_campo] não obedecer às regras de negócio.

                - PAGAMENTO_RECUSADO_DETENTORA - [Descrição do motivo de recusa].

                - PAGAMENTO_RECUSADO_SPI - [Código de erro conforme tabela de domínios reason PACS.002].

                - FALHA_INFRAESTRUTURA - [Descrição de qual falha na infraestrutura inviabilizou o processamento].

                - FALHA_INFRAESTRUTURA_SPI - Indica uma falha no Sistema de Pagamentos Instantâneos (SPI).

                - FALHA_INFRAESTRUTURA_DICT - Indica uma falha no Diretório de Identificadores de Contas Transacionais (DICT).

                - FALHA_INFRAESTRUTURA_ICP - Indica uma falha na Infraestrutura de Chaves Públicas (ICP).

                - FALHA_INFRAESTRUTURA_PSP_RECEBEDOR - Indica uma falha na infraestrutura do Prestador de Serviço de Pagamento
                (PSP) que recebe o pagamento.

                - FALHA_INFRAESTRUTURA_DETENTORA - indica uma falha na infraestrutura da instituição detentora das informações
                ou recursos.

                - CONTAS_ORIGEM_DESTINO_IGUAIS - Indica uma tentativa de pagamento onde a conta origem e a conta de destino são
                iguais.

                - FALHA_AGENDAMENTO_PAGAMENTOS - Falha ao agendar pagamentos.

                O rejectionReason FALHA_INFRAESTRUTURA não será excluído, apenas deixará de ser utilizado, permitindo assim,
                retrocompatibilidade e integridade entre os participantes.
                 Example: SALDO_INSUFICIENTE.
            detail (str): Contém informações adicionais ao pagamento rejeitado
    """

    code: EnumRejectionReasonTypeGetPix
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
        code = EnumRejectionReasonTypeGetPix(d.pop("code"))

        detail = d.pop("detail")

        rejection_reason_get_pix = cls(
            code=code,
            detail=detail,
        )

        rejection_reason_get_pix.additional_properties = d
        return rejection_reason_get_pix

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
