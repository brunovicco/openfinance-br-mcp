"""Payments API model: Objeto contendo as informações de consentimento para a iniciação de pagamento."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.business_entity import BusinessEntity
    from clients.payments_v4_0_0.models.create_payment_consent_data_payment import (
        CreatePaymentConsentDataPayment,
    )
    from clients.payments_v4_0_0.models.debtor_account import DebtorAccount
    from clients.payments_v4_0_0.models.identification import Identification
    from clients.payments_v4_0_0.models.logged_user import LoggedUser


T = TypeVar("T", bound="CreatePaymentConsentData")


@_attrs_define
class CreatePaymentConsentData:
    """Objeto contendo as informações de consentimento para a iniciação de pagamento.

    Attributes:
        logged_user (LoggedUser): Usuário (pessoa natural) que encontra-se logado na instituição Iniciadora de
            Pagamento.
        creditor (Identification): Objeto contendo os dados do recebedor (creditor).
        payment (CreatePaymentConsentDataPayment): Objeto contendo dados de pagamento para consentimento.
        business_entity (BusinessEntity | Unset): Usuário (pessoa jurídica) que encontra-se logado na instituição
            Iniciadora de Pagamento. [Restrição] Preenchimento obrigatório se usuário logado na instituição Iniciadora de
            Pagamento for um CNPJ (pessoa jurídica).
        debtor_account (DebtorAccount | Unset): Objeto que contém a identificação da conta de origem do pagador.
            As informações quanto à conta de origem do pagador poderão ser trazidas no consentimento para a detentora, caso
            a iniciadora tenha coletado essas informações do cliente. Do contrário, será coletada na detentora e trazida
            para a iniciadora como resposta à criação do pagamento.
    """

    logged_user: 'LoggedUser'
    creditor: 'Identification'
    payment: 'CreatePaymentConsentDataPayment'
    business_entity: 'BusinessEntity | Unset' = UNSET
    debtor_account: 'DebtorAccount | Unset' = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logged_user = self.logged_user.to_dict()

        creditor = self.creditor.to_dict()

        payment = self.payment.to_dict()

        business_entity: dict[str, Any] | Unset = UNSET
        if not isinstance(self.business_entity, Unset):
            business_entity = self.business_entity.to_dict()

        debtor_account: dict[str, Any] | Unset = UNSET
        if not isinstance(self.debtor_account, Unset):
            debtor_account = self.debtor_account.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "loggedUser": logged_user,
                "creditor": creditor,
                "payment": payment,
            }
        )
        if business_entity is not UNSET:
            field_dict["businessEntity"] = business_entity
        if debtor_account is not UNSET:
            field_dict["debtorAccount"] = debtor_account

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.business_entity import BusinessEntity
        from clients.payments_v4_0_0.models.create_payment_consent_data_payment import (
            CreatePaymentConsentDataPayment,
        )
        from clients.payments_v4_0_0.models.debtor_account import DebtorAccount
        from clients.payments_v4_0_0.models.identification import Identification
        from clients.payments_v4_0_0.models.logged_user import LoggedUser

        d = dict(src_dict)
        logged_user = LoggedUser.from_dict(d.pop("loggedUser"))

        creditor = Identification.from_dict(d.pop("creditor"))

        payment = CreatePaymentConsentDataPayment.from_dict(d.pop("payment"))

        _business_entity = d.pop("businessEntity", UNSET)
        business_entity: 'BusinessEntity | Unset'
        if isinstance(_business_entity, Unset):
            business_entity = UNSET
        else:
            business_entity = BusinessEntity.from_dict(_business_entity)

        _debtor_account = d.pop("debtorAccount", UNSET)
        debtor_account: 'DebtorAccount | Unset'
        if isinstance(_debtor_account, Unset):
            debtor_account = UNSET
        else:
            debtor_account = DebtorAccount.from_dict(_debtor_account)

        create_payment_consent_data = cls(
            logged_user=logged_user,
            creditor=creditor,
            payment=payment,
            business_entity=business_entity,
            debtor_account=debtor_account,
        )

        create_payment_consent_data.additional_properties = d
        return create_payment_consent_data

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
