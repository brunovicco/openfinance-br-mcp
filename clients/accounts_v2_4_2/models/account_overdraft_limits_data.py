"""Accounts API model: Conjunto de informações da Conta de: depósito à vista"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.accounts_v2_4_2.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.accounts_v2_4_2.models.account_overdraft_limits_data_overdraft_contracted_limit import (
        AccountOverdraftLimitsDataOverdraftContractedLimit,
    )
    from clients.accounts_v2_4_2.models.account_overdraft_limits_data_overdraft_used_limit import (
        AccountOverdraftLimitsDataOverdraftUsedLimit,
    )
    from clients.accounts_v2_4_2.models.account_overdraft_limits_data_unarranged_overdraft_amount import (
        AccountOverdraftLimitsDataUnarrangedOverdraftAmount,
    )


T = TypeVar("T", bound="AccountOverdraftLimitsData")


@_attrs_define
class AccountOverdraftLimitsData:
    """Conjunto de informações da Conta de: depósito à vista

    Attributes:
        overdraft_contracted_limit (AccountOverdraftLimitsDataOverdraftContractedLimit | Unset): Valor do limite
            contratado do cheque especial.
        overdraft_used_limit (AccountOverdraftLimitsDataOverdraftUsedLimit | Unset): Valor utilizado total do limite do
            cheque especial e o adiantamento a depositante.
        unarranged_overdraft_amount (AccountOverdraftLimitsDataUnarrangedOverdraftAmount | Unset): Valor de operação
            contratada em caráter emergencial para cobertura de saldo devedor em conta de depósitos à vista e de excesso
            sobre o limite pactuado de cheque especial.
    """

    overdraft_contracted_limit: (
        'AccountOverdraftLimitsDataOverdraftContractedLimit | Unset'
    ) = UNSET
    overdraft_used_limit: 'AccountOverdraftLimitsDataOverdraftUsedLimit | Unset' = UNSET
    unarranged_overdraft_amount: (
        'AccountOverdraftLimitsDataUnarrangedOverdraftAmount | Unset'
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        overdraft_contracted_limit: dict[str, Any] | Unset = UNSET
        if not isinstance(self.overdraft_contracted_limit, Unset):
            overdraft_contracted_limit = self.overdraft_contracted_limit.to_dict()

        overdraft_used_limit: dict[str, Any] | Unset = UNSET
        if not isinstance(self.overdraft_used_limit, Unset):
            overdraft_used_limit = self.overdraft_used_limit.to_dict()

        unarranged_overdraft_amount: dict[str, Any] | Unset = UNSET
        if not isinstance(self.unarranged_overdraft_amount, Unset):
            unarranged_overdraft_amount = self.unarranged_overdraft_amount.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if overdraft_contracted_limit is not UNSET:
            field_dict["overdraftContractedLimit"] = overdraft_contracted_limit
        if overdraft_used_limit is not UNSET:
            field_dict["overdraftUsedLimit"] = overdraft_used_limit
        if unarranged_overdraft_amount is not UNSET:
            field_dict["unarrangedOverdraftAmount"] = unarranged_overdraft_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.accounts_v2_4_2.models.account_overdraft_limits_data_overdraft_contracted_limit import (
            AccountOverdraftLimitsDataOverdraftContractedLimit,
        )
        from clients.accounts_v2_4_2.models.account_overdraft_limits_data_overdraft_used_limit import (
            AccountOverdraftLimitsDataOverdraftUsedLimit,
        )
        from clients.accounts_v2_4_2.models.account_overdraft_limits_data_unarranged_overdraft_amount import (
            AccountOverdraftLimitsDataUnarrangedOverdraftAmount,
        )

        d = dict(src_dict)
        _overdraft_contracted_limit = d.pop("overdraftContractedLimit", UNSET)
        overdraft_contracted_limit: (
            'AccountOverdraftLimitsDataOverdraftContractedLimit | Unset'
        )
        if isinstance(_overdraft_contracted_limit, Unset):
            overdraft_contracted_limit = UNSET
        else:
            overdraft_contracted_limit = (
                AccountOverdraftLimitsDataOverdraftContractedLimit.from_dict(
                    _overdraft_contracted_limit
                )
            )

        _overdraft_used_limit = d.pop("overdraftUsedLimit", UNSET)
        overdraft_used_limit: 'AccountOverdraftLimitsDataOverdraftUsedLimit | Unset'
        if isinstance(_overdraft_used_limit, Unset):
            overdraft_used_limit = UNSET
        else:
            overdraft_used_limit = (
                AccountOverdraftLimitsDataOverdraftUsedLimit.from_dict(
                    _overdraft_used_limit
                )
            )

        _unarranged_overdraft_amount = d.pop("unarrangedOverdraftAmount", UNSET)
        unarranged_overdraft_amount: (
            'AccountOverdraftLimitsDataUnarrangedOverdraftAmount | Unset'
        )
        if isinstance(_unarranged_overdraft_amount, Unset):
            unarranged_overdraft_amount = UNSET
        else:
            unarranged_overdraft_amount = (
                AccountOverdraftLimitsDataUnarrangedOverdraftAmount.from_dict(
                    _unarranged_overdraft_amount
                )
            )

        account_overdraft_limits_data = cls(
            overdraft_contracted_limit=overdraft_contracted_limit,
            overdraft_used_limit=overdraft_used_limit,
            unarranged_overdraft_amount=unarranged_overdraft_amount,
        )

        account_overdraft_limits_data.additional_properties = d
        return account_overdraft_limits_data

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
