"""Payments API model: Objeto que contém a identificação da conta de destino do beneficiário/recebedor."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_account_payments_type import EnumAccountPaymentsType
from clients.payments_v4_0_0.types import UNSET, Unset

T = TypeVar("T", bound="CreditorAccount")


@_attrs_define
class CreditorAccount:
    """Objeto que contém a identificação da conta de destino do beneficiário/recebedor.

    Attributes:
        ispb (str): Deve ser preenchido com o ISPB (Identificador do Sistema de Pagamentos Brasileiros) do participante
            do SPI (Sistema de pagamentos instantâneos) somente com números.
             Example: 12345678.
        number (str): Deve ser preenchido com o número da conta do usuário recebedor, com dígito verificador (se este
            existir),
            se houver valor alfanumérico, este deve ser convertido para 0.
             Example: 1234567890.
        account_type (EnumAccountPaymentsType): Tipos de contas usadas para pagamento.
            Modalidades tradicionais previstas pela Resolução 4.753, não contemplando contas vinculadas,
            conta de domiciliados no exterior, contas em moedas estrangeiras e conta correspondente moeda eletrônica.
            Segue descrição de cada valor do ENUM.

            - CACC - Current - Conta Corrente.
            - SVGS - Savings - Conta de Poupança.
            - TRAN - TransactingAccount - Conta de Pagamento pré-paga.
             Example: CACC.
        issuer (str | Unset): Código da Agência emissora da conta sem dígito.
            (Agência é a dependência destinada ao atendimento aos clientes, ao público em geral e aos associados de
            cooperativas de crédito,
            no exercício de atividades da instituição, não podendo ser móvel ou transitória).

            [Restrição] Preenchimento obrigatório para os seguintes tipos de conta: CACC (CONTA_DEPOSITO_A_VISTA) e SVGS
            (CONTA_POUPANCA).
             Example: 1774.
    """

    ispb: str
    number: str
    account_type: EnumAccountPaymentsType
    issuer: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ispb = self.ispb

        number = self.number

        account_type = self.account_type.value

        issuer = self.issuer

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ispb": ispb,
                "number": number,
                "accountType": account_type,
            }
        )
        if issuer is not UNSET:
            field_dict["issuer"] = issuer

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ispb = d.pop("ispb")

        number = d.pop("number")

        account_type = EnumAccountPaymentsType(d.pop("accountType"))

        issuer = d.pop("issuer", UNSET)

        creditor_account = cls(
            ispb=ispb,
            number=number,
            account_type=account_type,
            issuer=issuer,
        )

        creditor_account.additional_properties = d
        return creditor_account

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
