"""Payments API model: Objeto contendo dados do pagameto como moeda e valor."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PaymentPix")


@_attrs_define
class PaymentPix:
    """Objeto contendo dados do pagameto como moeda e valor.

    Attributes:
        amount (str): Valor da transação com 2 casas decimais. O valor deve ser o mesmo enviado no consentimento.

            Para QR Code estático com valor pré-determinado no QR Code ou para QR Code dinâmico com indicação de que o valor
            não pode ser alterado: O campo amount deve ser preenchido com o valor estabelecido no QR Code.
            Caso seja preenchido com valor divergente do QR Code, deve ser retornado um erro HTTP Status 422.
             Example: 100000.12.
        currency (str): Código da moeda nacional segundo modelo ISO-4217, ou seja, 'BRL'.
            Todos os valores monetários informados estão representados com a moeda vigente do Brasil.
             Example: BRL.
    """

    amount: str
    currency: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        currency = self.currency

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "currency": currency,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount")

        currency = d.pop("currency")

        payment_pix = cls(
            amount=amount,
            currency=currency,
        )

        payment_pix.additional_properties = d
        return payment_pix

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
