"""Consents API model: Define a razão pela qual o consentimento foi rejeitado."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.consents_v3_3_1.models.response_consent_read_data_rejection_reason_code import (
    ResponseConsentReadDataRejectionReasonCode,
)
from clients.consents_v3_3_1.types import UNSET, Unset

T = TypeVar("T", bound="ResponseConsentReadDataRejectionReason")


@_attrs_define
class ResponseConsentReadDataRejectionReason:
    """Define a razão pela qual o consentimento foi rejeitado.

    Attributes:
        code (ResponseConsentReadDataRejectionReasonCode): Define o código da razão pela qual o consentimento foi
            rejeitado.

            - CONSENT_EXPIRED – consentimento que ultrapassou o tempo limite para autorização.
            - CUSTOMER_MANUALLY_REJECTED – cliente efetuou a rejeição do consentimento manualmente através de interação nas
            instituições participantes.
            - CUSTOMER_MANUALLY_REVOKED – cliente efetuou a revogação após a autorização do consentimento.
            - CONSENT_MAX_DATE_REACHED – consentimento que ultrapassou o tempo limite de compartilhamento.
            - CONSENT_TECHNICAL_ISSUE – consentimento que foi rejeitado devido a um problema técnico que impossibilita seu
            uso pela instituição receptora, por exemplo: falha associada a troca do AuthCode pelo AccessToken, durante o
            processo de Hybrid Flow.
            - INTERNAL_SECURITY_REASON – consentimento que foi rejeitado devido as políticas de segurança aplicada pela
            instituição transmissora.
             Example: CONSENT_EXPIRED.
        additional_information (str | Unset): Contém informações adicionais a critério da transmissora. Example: Tempo
            de confirmação da múltipla alçada excedido..
    """

    code: ResponseConsentReadDataRejectionReasonCode
    additional_information: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code.value

        additional_information = self.additional_information

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
            }
        )
        if additional_information is not UNSET:
            field_dict["additionalInformation"] = additional_information

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = ResponseConsentReadDataRejectionReasonCode(d.pop("code"))

        additional_information = d.pop("additionalInformation", UNSET)

        response_consent_read_data_rejection_reason = cls(
            code=code,
            additional_information=additional_information,
        )

        response_consent_read_data_rejection_reason.additional_properties = d
        return response_consent_read_data_rejection_reason

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
