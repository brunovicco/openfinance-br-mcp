"""Credit Cards Accounts API model: Conjunto de informações das Contas de pagamento pós paga"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.credit_cards_v2_3_1.models.enum_credit_card_account_network import EnumCreditCardAccountNetwork
from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_product_type import (
    EnumCreditCardAccountsProductType,
)
from clients.credit_cards_v2_3_1.types import UNSET, Unset

T = TypeVar("T", bound="CreditCardAccountsData")


@_attrs_define
class CreditCardAccountsData:
    """Conjunto de informações das Contas de pagamento pós paga

    Attributes:
        credit_card_account_id (str): Identifica de forma única a conta pagamento pós-paga do cliente, mantendo as
            regras de imutabilidade dentro da instituição transmissora. Example: XXZTR3459087.
        brand_name (str): Nome da Marca reportada pelo participante no Open Finance. Recomenda-se utilizar, sempre que
            possível, o mesmo nome de marca atribuído no campo do diretório Customer Friendly Server Name (Authorisation
            Server). Example: Organização A.
        company_cnpj (str): Número completo do CNPJ da instituição responsável pelo Cadastro - o CNPJ corresponde ao
            número de inscrição no Cadastro de Pessoa Jurídica. Deve-se ter apenas os números do CNPJ, sem máscara Example:
            21128159000166.
        name (str): Denominação/Identificação do nome da conta de pagamento pós-paga (cartão). Conforme CIRCULAR Nº
            3.680,BCB, 2013: 'conta de pagamento pós-paga: destinada à execução de transações de pagamento que independem do
            aporte prévio de recursos Example: Cartão Universitário.
        product_type (EnumCreditCardAccountsProductType): Categoria atribuída a um cartão de pagamento, sob uma certa
            denominação, que lhe agrega um conjunto de vantagens, diferenciando-o de acordo com o perfil do portador.
            Example: OUTROS.
        credit_card_network (EnumCreditCardAccountNetwork): Categoria de Bandeiras de Cartões de Crédito (Instituidor do
            arranjo de pagamento).
            Bandeira é a detentora de todos os direitos e deveres da utilização da marca estampada no cartão, inclusive as
            bandeiras pertencentes aos emissores.
             Example: VISA.
        product_additional_info (str | Unset): Informações complementares se tipo de Cartão 'OUTROS'
        network_additional_info (str | Unset): Texto livre para especificar categoria de bandeira marcada como 'OUTRAS'
            Example: AURA CARD.
    """

    credit_card_account_id: str
    brand_name: str
    company_cnpj: str
    name: str
    product_type: EnumCreditCardAccountsProductType
    credit_card_network: EnumCreditCardAccountNetwork
    product_additional_info: str | Unset = UNSET
    network_additional_info: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        credit_card_account_id = self.credit_card_account_id

        brand_name = self.brand_name

        company_cnpj = self.company_cnpj

        name = self.name

        product_type = self.product_type.value

        credit_card_network = self.credit_card_network.value

        product_additional_info = self.product_additional_info

        network_additional_info = self.network_additional_info

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "creditCardAccountId": credit_card_account_id,
                "brandName": brand_name,
                "companyCnpj": company_cnpj,
                "name": name,
                "productType": product_type,
                "creditCardNetwork": credit_card_network,
            }
        )
        if product_additional_info is not UNSET:
            field_dict["productAdditionalInfo"] = product_additional_info
        if network_additional_info is not UNSET:
            field_dict["networkAdditionalInfo"] = network_additional_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        credit_card_account_id = d.pop("creditCardAccountId")

        brand_name = d.pop("brandName")

        company_cnpj = d.pop("companyCnpj")

        name = d.pop("name")

        product_type = EnumCreditCardAccountsProductType(d.pop("productType"))

        credit_card_network = EnumCreditCardAccountNetwork(d.pop("creditCardNetwork"))

        product_additional_info = d.pop("productAdditionalInfo", UNSET)

        network_additional_info = d.pop("networkAdditionalInfo", UNSET)

        credit_card_accounts_data = cls(
            credit_card_account_id=credit_card_account_id,
            brand_name=brand_name,
            company_cnpj=company_cnpj,
            name=name,
            product_type=product_type,
            credit_card_network=credit_card_network,
            product_additional_info=product_additional_info,
            network_additional_info=network_additional_info,
        )

        credit_card_accounts_data.additional_properties = d
        return credit_card_accounts_data

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
