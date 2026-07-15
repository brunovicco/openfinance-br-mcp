"""Consents API model: Objeto a ser retornado caso o consentimento seja rejeitado."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.consents_v3_3_1.models.enum_rejected_by import EnumRejectedBy

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.response_consent_read_data_rejection_reason import (
        ResponseConsentReadDataRejectionReason,
    )


T = TypeVar("T", bound="ResponseConsentReadDataRejection")


@_attrs_define
class ResponseConsentReadDataRejection:
    """Objeto a ser retornado caso o consentimento seja rejeitado.

    Attributes:
        rejected_by (EnumRejectedBy): Informar usuário responsável pela rejeição.
            1. USER usuário
            2. ASPSP instituição transmissora
            3. TPP instituição receptora
             Example: USER.
        reason (ResponseConsentReadDataRejectionReason): Define a razão pela qual o consentimento foi rejeitado.
    """

    rejected_by: EnumRejectedBy
    reason: 'ResponseConsentReadDataRejectionReason'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rejected_by = self.rejected_by.value

        reason = self.reason.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rejectedBy": rejected_by,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.response_consent_read_data_rejection_reason import (
            ResponseConsentReadDataRejectionReason,
        )

        d = dict(src_dict)
        rejected_by = EnumRejectedBy(d.pop("rejectedBy"))

        reason = ResponseConsentReadDataRejectionReason.from_dict(d.pop("reason"))

        response_consent_read_data_rejection = cls(
            rejected_by=rejected_by,
            reason=reason,
        )

        response_consent_read_data_rejection.additional_properties = d
        return response_consent_read_data_rejection

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
