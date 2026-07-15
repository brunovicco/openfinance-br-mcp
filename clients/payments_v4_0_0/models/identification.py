"""Payments API model: Objeto contendo os dados do recebedor (creditor)."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_payment_person_type import EnumPaymentPersonType

T = TypeVar("T", bound="Identification")


@_attrs_define
class Identification:
    """Objeto contendo os dados do recebedor (creditor).

    Attributes:
        person_type (EnumPaymentPersonType): Titular, pessoa natural ou juridica a quem se referem os dados de recebedor
            (creditor).
        cpf_cnpj (str): Identificação da pessoa envolvida na transação.
            Preencher com o CPF ou CNPJ, de acordo com o valor escolhido no campo type.
            O CPF será utilizado com 11 números e deverá ser informado sem pontos ou traços.
            O CNPJ será utilizado com 14 números e deverá ser informado sem pontos ou traços.
             Example: 58764789000137.
        name (str): Em caso de pessoa natural deve ser informado o nome completo do titular da conta do recebedor.
            Em caso de pessoa jurídica deve ser informada a razão social ou o nome fantasia da conta do recebedor.
             Example: Marco Antonio de Brito.
    """

    person_type: EnumPaymentPersonType
    cpf_cnpj: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        person_type = self.person_type.value

        cpf_cnpj = self.cpf_cnpj

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "personType": person_type,
                "cpfCnpj": cpf_cnpj,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        person_type = EnumPaymentPersonType(d.pop("personType"))

        cpf_cnpj = d.pop("cpfCnpj")

        name = d.pop("name")

        identification = cls(
            person_type=person_type,
            cpf_cnpj=cpf_cnpj,
            name=name,
        )

        identification.additional_properties = d
        return identification

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
