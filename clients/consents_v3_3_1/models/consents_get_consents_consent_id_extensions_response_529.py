"""ConsentsGetConsentsConsentIdExtensionsResponse529: a data model of the Consents API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from clients.consents_v3_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529_errors_item import (
        ConsentsGetConsentsConsentIdExtensionsResponse529ErrorsItem,
    )
    from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529_meta import (
        ConsentsGetConsentsConsentIdExtensionsResponse529Meta,
    )


T = TypeVar("T", bound="ConsentsGetConsentsConsentIdExtensionsResponse529")


@_attrs_define
class ConsentsGetConsentsConsentIdExtensionsResponse529:
    """
    Attributes:
        errors (list[ConsentsGetConsentsConsentIdExtensionsResponse529ErrorsItem]):
        meta (ConsentsGetConsentsConsentIdExtensionsResponse529Meta | Unset): Meta informações referente a API
            requisitada.
    """

    errors: 'list[ConsentsGetConsentsConsentIdExtensionsResponse529ErrorsItem]'
    meta: 'ConsentsGetConsentsConsentIdExtensionsResponse529Meta | Unset' = UNSET

    def to_dict(self) -> dict[str, Any]:
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "errors": errors,
            }
        )
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529_errors_item import (
            ConsentsGetConsentsConsentIdExtensionsResponse529ErrorsItem,
        )
        from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529_meta import (
            ConsentsGetConsentsConsentIdExtensionsResponse529Meta,
        )

        d = dict(src_dict)
        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = (
                ConsentsGetConsentsConsentIdExtensionsResponse529ErrorsItem.from_dict(
                    errors_item_data
                )
            )

            errors.append(errors_item)

        _meta = d.pop("meta", UNSET)
        meta: 'ConsentsGetConsentsConsentIdExtensionsResponse529Meta | Unset'
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = ConsentsGetConsentsConsentIdExtensionsResponse529Meta.from_dict(
                _meta
            )

        consents_get_consents_consent_id_extensions_response_529 = cls(
            errors=errors,
            meta=meta,
        )

        return consents_get_consents_consent_id_extensions_response_529
