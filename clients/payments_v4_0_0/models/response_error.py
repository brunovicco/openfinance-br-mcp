"""ResponseError: a data model of the Payments API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.response_error_errors_item import ResponseErrorErrorsItem
    from clients.payments_v4_0_0.models.response_error_meta import ResponseErrorMeta


T = TypeVar("T", bound="ResponseError")


@_attrs_define
class ResponseError:
    """
    Attributes:
        errors (list[ResponseErrorErrorsItem]):
        meta (ResponseErrorMeta | Unset): Meta informações referente à API requisitada.
    """

    errors: 'list[ResponseErrorErrorsItem]'
    meta: 'ResponseErrorMeta | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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
        from clients.payments_v4_0_0.models.response_error_errors_item import ResponseErrorErrorsItem
        from clients.payments_v4_0_0.models.response_error_meta import ResponseErrorMeta

        d = dict(src_dict)
        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = ResponseErrorErrorsItem.from_dict(errors_item_data)

            errors.append(errors_item)

        _meta = d.pop("meta", UNSET)
        meta: 'ResponseErrorMeta | Unset'
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = ResponseErrorMeta.from_dict(_meta)

        response_error = cls(
            errors=errors,
            meta=meta,
        )

        response_error.additional_properties = d
        return response_error

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
