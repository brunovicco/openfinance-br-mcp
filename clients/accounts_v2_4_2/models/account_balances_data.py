"""Accounts API model: Conjunto de informações das Contas de: depósito à vista, poupança e de pagamento pré-paga"""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from clients.accounts_v2_4_2.models.account_balances_data_automatically_invested_amount import (
        AccountBalancesDataAutomaticallyInvestedAmount,
    )
    from clients.accounts_v2_4_2.models.account_balances_data_available_amount import (
        AccountBalancesDataAvailableAmount,
    )
    from clients.accounts_v2_4_2.models.account_balances_data_blocked_amount import (
        AccountBalancesDataBlockedAmount,
    )


T = TypeVar("T", bound="AccountBalancesData")


@_attrs_define
class AccountBalancesData:
    """Conjunto de informações das Contas de: depósito à vista, poupança e de pagamento pré-paga

    Attributes:
        available_amount (AccountBalancesDataAvailableAmount): Saldo disponível para utilização imediata. No caso de
            conta de depósito a vista, sem considerar cheque especial e investimentos atrelados a conta. Expresso em valor
            monetário com no mínimo 2 casas e no máximo 4 casas decimais.
        blocked_amount (AccountBalancesDataBlockedAmount): Saldo bloqueado, não disponível para utilização imediata, por
            motivo de bloqueio apresentado para o cliente nos canais eletrônicos. Expresso em valor monetário com no mínimo
            2 casas e no máximo 4 casas decimais.
        automatically_invested_amount (AccountBalancesDataAutomaticallyInvestedAmount): Saldo disponível com aplicação
            automática - corresponde a soma do saldo disponível acrescido do valor obtido a partir da aplicação automática.
            Expresso em valor monetário com no mínimo 2 casas e no máximo 4 casas decimais.
        update_date_time (datetime.datetime): Data e hora da última atualização do saldo. É esperado que a instituição
            informe a última vez que capturou o saldo para compartilhamento no Open Finance. Dessa forma, é possível que:
            - Caso a instituição capture dados de forma síncrona essa informação seja de poucos momentos;
            - Caso a instituição capture dados de forma assíncrona essa informação seja de horas ou dias no passado;
            - Quando não existente uma data vinculada especificamente ao bloco, se assume a data e hora de atualização do
            cadastro como um todo.

            De toda forma, é preciso continuar respeitando o prazo máximo de tempestividade da API de Contas.
             Example: 2021-05-21T08:30:00Z.
    """

    available_amount: "AccountBalancesDataAvailableAmount"
    blocked_amount: "AccountBalancesDataBlockedAmount"
    automatically_invested_amount: "AccountBalancesDataAutomaticallyInvestedAmount"
    update_date_time: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        available_amount = self.available_amount.to_dict()

        blocked_amount = self.blocked_amount.to_dict()

        automatically_invested_amount = self.automatically_invested_amount.to_dict()

        update_date_time = self.update_date_time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "availableAmount": available_amount,
                "blockedAmount": blocked_amount,
                "automaticallyInvestedAmount": automatically_invested_amount,
                "updateDateTime": update_date_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.accounts_v2_4_2.models.account_balances_data_automatically_invested_amount import (
            AccountBalancesDataAutomaticallyInvestedAmount,
        )
        from clients.accounts_v2_4_2.models.account_balances_data_available_amount import (
            AccountBalancesDataAvailableAmount,
        )
        from clients.accounts_v2_4_2.models.account_balances_data_blocked_amount import (
            AccountBalancesDataBlockedAmount,
        )

        d = dict(src_dict)
        available_amount = AccountBalancesDataAvailableAmount.from_dict(
            d.pop("availableAmount")
        )

        blocked_amount = AccountBalancesDataBlockedAmount.from_dict(
            d.pop("blockedAmount")
        )

        automatically_invested_amount = (
            AccountBalancesDataAutomaticallyInvestedAmount.from_dict(
                d.pop("automaticallyInvestedAmount")
            )
        )

        update_date_time = isoparse(d.pop("updateDateTime"))

        account_balances_data = cls(
            available_amount=available_amount,
            blocked_amount=blocked_amount,
            automatically_invested_amount=automatically_invested_amount,
            update_date_time=update_date_time,
        )

        account_balances_data.additional_properties = d
        return account_balances_data

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
