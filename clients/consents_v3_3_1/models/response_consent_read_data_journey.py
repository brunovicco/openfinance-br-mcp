"""Consents API model: Informações adicionais sobre o contexto de Jornada Otimizada. [RESTRIÇÃO] Objeto de envio obrigatório quando o"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.consents_v3_3_1.types import UNSET, Unset

T = TypeVar("T", bound="ResponseConsentReadDataJourney")


@_attrs_define
class ResponseConsentReadDataJourney:
    """Informações adicionais sobre o contexto de Jornada Otimizada. [RESTRIÇÃO] Objeto de envio obrigatório quando o
    usuário manifestar consentimento para compartilhamento de saldo  através da Jornada Otimizada.

        Attributes:
            is_linked (bool | Unset): Campo para identificação de consentimento iniciado em Jornada Otimizada. [RESTRIÇÃO]
                Campo de preenchimento obrigatório para todo consentimento iniciado a partir da jornada otimizada, independente
                do status do consentimento.
                 Example: True.
            link_id (str | Unset): Identificador do consentimento de pagamento/vínculo ao qual este consentimento está
                vinculado. [RESTRIÇÃO] Esse campo será preenchido caso o consentimento tenha sido autorizado ou rejeitado por
                ação do cliente.
                 Example: urn:bancoex:C1DD331237.
    """

    is_linked: bool | Unset = UNSET
    link_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_linked = self.is_linked

        link_id = self.link_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_linked is not UNSET:
            field_dict["isLinked"] = is_linked
        if link_id is not UNSET:
            field_dict["linkId"] = link_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_linked = d.pop("isLinked", UNSET)

        link_id = d.pop("linkId", UNSET)

        response_consent_read_data_journey = cls(
            is_linked=is_linked,
            link_id=link_id,
        )

        response_consent_read_data_journey.additional_properties = d
        return response_consent_read_data_journey

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
