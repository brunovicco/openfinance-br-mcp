"""VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.variable_incomes_v1_3_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.variable_incomes_v1_3_0.models.variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423_errors_item import (
        VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423ErrorsItem,
    )
    from clients.variable_incomes_v1_3_0.models.variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423_meta import (
        VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423Meta,
    )


T = TypeVar(
    "T",
    bound="VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423",
)


@_attrs_define
class VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423:
    """
    Attributes:
        errors (list[VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423ErrorsItem]):
        meta (VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423Meta | Unset): Meta informações
            referente à API requisitada.
    """

    errors: 'list[ VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423ErrorsItem ]'
    meta: (
        'VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423Meta | Unset'
    ) = UNSET
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
        from clients.variable_incomes_v1_3_0.models.variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423_errors_item import (
            VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423ErrorsItem,
        )
        from clients.variable_incomes_v1_3_0.models.variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423_meta import (
            VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423Meta,
        )

        d = dict(src_dict)
        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423ErrorsItem.from_dict(
                errors_item_data
            )

            errors.append(errors_item)

        _meta = d.pop("meta", UNSET)
        meta: (
            'VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423Meta | Unset'
        )
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423Meta.from_dict(
                _meta
            )

        variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423 = cls(
            errors=errors,
            meta=meta,
        )

        variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423.additional_properties = d
        return variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423

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
