"""Credit Cards Accounts API model: Conjunto de informações relativas aos Meios de Pagamento da Conta de pagamento pós-paga"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreditCardsAccountPaymentMethod")


@_attrs_define
class CreditCardsAccountPaymentMethod:
    """Conjunto de informações relativas aos Meios de Pagamento da Conta de pagamento pós-paga

    Attributes:
        identification_number (str): Número de identificação do cartão: corresponde aos 4 últimos dígitos do cartão para
            pessoa natural, ou então, preencher com um identificador para pessoa jurídica, com as características definidas
            para os IDs no Open Finance.
             Example: 4453.
        is_multiple_credit_card (bool): Indica se o Cartão de crédito associado à conta pagamento pós-paga é múltiplo ou
            não. Cartões denominados múltiplos possuem tanto a função crédito quanto a função débito, devendo o proprietário
            do cartão, no momento de sua utilização, informar se o pagamento é na função crédito (que leva a um pagamento
            futuro, por meio de uma fatura do cartão de crédito) ou na função débito.
             Example: True.
    """

    identification_number: str
    is_multiple_credit_card: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identification_number = self.identification_number

        is_multiple_credit_card = self.is_multiple_credit_card

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identificationNumber": identification_number,
                "isMultipleCreditCard": is_multiple_credit_card,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identification_number = d.pop("identificationNumber")

        is_multiple_credit_card = d.pop("isMultipleCreditCard")

        credit_cards_account_payment_method = cls(
            identification_number=identification_number,
            is_multiple_credit_card=is_multiple_credit_card,
        )

        credit_cards_account_payment_method.additional_properties = d
        return credit_cards_account_payment_method

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
