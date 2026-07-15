"""Payments API model: Objeto contendo os detalhes do pagamento."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.payments_v4_0_0.models.enum_local_instrument import EnumLocalInstrument
from clients.payments_v4_0_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.creditor_account import CreditorAccount


T = TypeVar("T", bound="Details")


@_attrs_define
class Details:
    """Objeto contendo os detalhes do pagamento.

    Attributes:
        local_instrument (EnumLocalInstrument): Especifica a forma de iniciação do pagamento:
            - MANU - Inserção manual de dados da conta transacional
            - DICT - Inserção manual de chave Pix
            - QRDN - QR code dinâmico
            - QRES - QR code estático
            - INIC - Indica que o recebedor (creditor) contratou o Iniciador de Pagamentos especificamente para realizar
            iniciações de pagamento em que o beneficiário é previamente conhecido.

            [Restrição] Se /data/payment/schedule enviado com valor diferente de single durante a criação do consentimento,
            apenas os métodos MANU, DICT ou QRES são permitidos.
             Example: DICT.
        creditor_account (CreditorAccount): Objeto que contém a identificação da conta de destino do
            beneficiário/recebedor.
        qr_code (str | Unset): Sequência de caracteres que corresponde ao QR Code disponibilizado para o pagador.
            É a sequência de caracteres que seria lida pelo leitor de QR Code, e deve propiciar o retorno dos dados do
            pagador após consulta na DICT.
            Essa funcionalidade é possível tanto para QR Code estático quanto para QR Code dinâmico.
            No arranjo do Pix esta é a mesma sequência gerada e/ou lida pela funcionalidade Pix Copia e Cola.
            Este campo deverá ser no formato UTF-8.
            [Restrição] Preenchimento obrigatório para pagamentos por QR Code, observado o tamanho máximo de 512 bytes.
             Example: 00020104141234567890123426660014BR.GOV.BCB.PIX014466756C616E6F32303139406578616D706C652E636F6D27300012
            BR.COM.OUTRO011001234567895204000053039865406123.455802BR5915NOMEDORECEBEDOR6008BRASILIA61087007490062
            530515RP12345678-201950300017BR.GOV.BCB.BRCODE01051.0.080450014BR.GOV.BCB.PIX0123PADRAO.URL.PIX/0123AB
            CD81390012BR.COM.OUTRO01190123.ABCD.3456.WXYZ6304EB76
            .
        proxy (str | Unset): Chave cadastrada no DICT pertencente ao recebedor. Os tipos de chaves podem ser: telefone,
            e-mail, cpf/cnpj ou chave aleatória.
            No caso de telefone celular deve ser informado no padrão E.1641.
            Para e-mail deve ter o formato xxxxxxxx@xxxxxxx.xxx(.xx) e no máximo 77 caracteres.
            No caso de CPF deverá ser informado com 11 números, sem pontos ou traços.
            Para o caso de CNPJ deverá ser informado com 14 números, sem pontos ou traços.
            No caso de chave aleatória deve ser informado o UUID gerado pelo DICT, conforme formato especificado na
            RFC41223.
            Se informado, a detentora da conta deve validar o proxy no DICT quando localInstrument for igual a DICT, QRDN ou
            QRES e validar o campo creditorAccount.
            Esta validação é opcional caso o localInstrument for igual a INIC.
            [Restrição]
            Se localInstrument for igual a MANU, o campo proxy não deve ser preenchido.
            Se localInstrument for igual INIC, DICT, QRDN ou QRES, o campo proxy deve ser sempre preenchido com a chave Pix.
             Example: 12345678901.
    """

    local_instrument: EnumLocalInstrument
    creditor_account: 'CreditorAccount'
    qr_code: str | Unset = UNSET
    proxy: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        local_instrument = self.local_instrument.value

        creditor_account = self.creditor_account.to_dict()

        qr_code = self.qr_code

        proxy = self.proxy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "localInstrument": local_instrument,
                "creditorAccount": creditor_account,
            }
        )
        if qr_code is not UNSET:
            field_dict["qrCode"] = qr_code
        if proxy is not UNSET:
            field_dict["proxy"] = proxy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.creditor_account import CreditorAccount

        d = dict(src_dict)
        local_instrument = EnumLocalInstrument(d.pop("localInstrument"))

        creditor_account = CreditorAccount.from_dict(d.pop("creditorAccount"))

        qr_code = d.pop("qrCode", UNSET)

        proxy = d.pop("proxy", UNSET)

        details = cls(
            local_instrument=local_instrument,
            creditor_account=creditor_account,
            qr_code=qr_code,
            proxy=proxy,
        )

        details.additional_properties = d
        return details

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
