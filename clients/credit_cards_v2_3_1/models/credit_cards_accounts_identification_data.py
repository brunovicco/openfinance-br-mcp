"""Credit Cards Accounts API model: Conjunto de informações referentes à identificação da conta de pagamento pós-paga."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.credit_cards_v2_3_1.models.enum_credit_card_account_network import EnumCreditCardAccountNetwork
from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_product_type import (
    EnumCreditCardAccountsProductType,
)
from clients.credit_cards_v2_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.credit_cards_v2_3_1.models.credit_cards_account_payment_method import (
        CreditCardsAccountPaymentMethod,
    )


T = TypeVar("T", bound="CreditCardsAccountsIdentificationData")


@_attrs_define
class CreditCardsAccountsIdentificationData:
    """Conjunto de informações referentes à identificação da conta de pagamento pós-paga.

    Attributes:
        name (str): Denominação/Identificação do nome da conta de pagamento pós-paga (cartão). Conforme CIRCULAR Nº
            3.680,BCB, 2013: 'conta de pagamento pós-paga: destinada à execução de transações de pagamento que independem do
            aporte prévio de recursos'.
             Example: Cartão Universitário.
        product_type (EnumCreditCardAccountsProductType): Categoria atribuída a um cartão de pagamento, sob uma certa
            denominação, que lhe agrega um conjunto de vantagens, diferenciando-o de acordo com o perfil do portador.
            Example: OUTROS.
        credit_card_network (EnumCreditCardAccountNetwork): Categoria de Bandeiras de Cartões de Crédito (Instituidor do
            arranjo de pagamento).
            Bandeira é a detentora de todos os direitos e deveres da utilização da marca estampada no cartão, inclusive as
            bandeiras pertencentes aos emissores.
             Example: VISA.
        payment_method (list[CreditCardsAccountPaymentMethod]): Listagem dos cartões (ex.: virtual/adicional/titular)
            associados a conta cartão consentida, conforme disponíveis ao usuário nos canais proprietários.
        product_additional_info (str | Unset): Informações complementares se tipo de Cartão 'OUTROS' Example:
            OURO_INTERNACIONAL.
        network_additional_info (str | Unset): Texto livre para especificar categoria de bandeira marcada como 'OUTRAS'.
            Example: AURA CARD.
    """

    name: str
    product_type: EnumCreditCardAccountsProductType
    credit_card_network: EnumCreditCardAccountNetwork
    payment_method: 'list[CreditCardsAccountPaymentMethod]'
    product_additional_info: str | Unset = UNSET
    network_additional_info: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        product_type = self.product_type.value

        credit_card_network = self.credit_card_network.value

        payment_method = []
        for payment_method_item_data in self.payment_method:
            payment_method_item = payment_method_item_data.to_dict()
            payment_method.append(payment_method_item)

        product_additional_info = self.product_additional_info

        network_additional_info = self.network_additional_info

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "productType": product_type,
                "creditCardNetwork": credit_card_network,
                "paymentMethod": payment_method,
            }
        )
        if product_additional_info is not UNSET:
            field_dict["productAdditionalInfo"] = product_additional_info
        if network_additional_info is not UNSET:
            field_dict["networkAdditionalInfo"] = network_additional_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.credit_cards_v2_3_1.models.credit_cards_account_payment_method import (
            CreditCardsAccountPaymentMethod,
        )

        d = dict(src_dict)
        name = d.pop("name")

        product_type = EnumCreditCardAccountsProductType(d.pop("productType"))

        credit_card_network = EnumCreditCardAccountNetwork(d.pop("creditCardNetwork"))

        payment_method = []
        _payment_method = d.pop("paymentMethod")
        for payment_method_item_data in _payment_method:
            payment_method_item = CreditCardsAccountPaymentMethod.from_dict(
                payment_method_item_data
            )

            payment_method.append(payment_method_item)

        product_additional_info = d.pop("productAdditionalInfo", UNSET)

        network_additional_info = d.pop("networkAdditionalInfo", UNSET)

        credit_cards_accounts_identification_data = cls(
            name=name,
            product_type=product_type,
            credit_card_network=credit_card_network,
            payment_method=payment_method,
            product_additional_info=product_additional_info,
            network_additional_info=network_additional_info,
        )

        credit_cards_accounts_identification_data.additional_properties = d
        return credit_cards_accounts_identification_data

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
