"""AccountData: a data model of the Accounts API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.accounts_v2_4_2.models.enum_account_type import EnumAccountType
from clients.accounts_v2_4_2.types import UNSET, Unset

T = TypeVar("T", bound="AccountData")


@_attrs_define
class AccountData:
    """
    Attributes:
        brand_name (str): Nome da Marca reportada pelo participante no Open Finance. Recomenda-se utilizar, sempre que
            possível, o mesmo nome de marca atribuído no campo do diretório Customer Friendly Server Name (Authorisation
            Server). Example: Organização A.
        company_cnpj (str): Número completo do CNPJ da instituição responsável pelo Cadastro - o CNPJ corresponde ao
            número de inscrição no Cadastro de Pessoa Jurídica. Deve-se ter apenas os números do CNPJ, sem máscara Example:
            21128159000166.
        type_ (EnumAccountType): Tipos de contas. Modalidades tradicionais previstas pela Resolução 4.753, não
            contemplando contas vinculadas, conta de domiciliados no exterior, contas em moedas estrangeiras e conta
            correspondente moeda eletrônica. Vide Enum
            Conta de depósito à vista ou Conta corrente - é o tipo mais comum. Nela, o dinheiro fica à sua disposição para
            ser sacado a qualquer momento. Essa conta não gera rendimentos para o depositante
            Conta poupança - foi criada para estimular as pessoas a pouparem. O dinheiro que ficar na conta por trinta dias
            passa a gerar rendimentos, com isenção de imposto de renda para quem declara. Ou seja, o dinheiro “cresce”
            (rende) enquanto ficar guardado na conta. Cada depósito terá rendimentos de mês em mês, sempre no dia do mês em
            que o dinheiro tiver sido depositado
            Conta de pagamento pré-paga: segundo CIRCULAR Nº 3.680, BCB de  2013, é a 'destinada à execução de transações de
            pagamento em moeda eletrônica realizadas com base em fundos denominados em reais previamente aportados'
             Example: CONTA_DEPOSITO_A_VISTA.
        compe_code (str): Código identificador atribuído pelo Banco Central do Brasil às instituições participantes do
            STR (Sistema de Transferência de reservas).O Compe (Sistema de Compensação de Cheques e Outros Papéis) é um
            sistema que identifica e processa as compensações bancárias. Ele é representado por um código de três dígitos
            que serve como identificador de bancos, sendo assim, cada instituição bancária possui um número exclusivo
            Example: 001.
        number (str): Número da conta Example: 94088392.
        check_digit (str): Dígito da conta Example: 4.
        account_id (str): Identifica de forma única  a conta do cliente, mantendo as regras de imutabilidade dentro da
            instituição transmissora. Example: 92792126019929279212650822221989319252576.
        branch_code (str | Unset): Código da Agência detentora da conta. (Agência é a dependência destinada ao
            atendimento aos clientes, ao público em geral e aos associados de cooperativas de crédito, no exercício de
            atividades da instituição, não podendo ser móvel ou transitória)

            [Restrição] Obrigatoriamente deve ser preenchido quando o campo "type" for diferente de
            CONTA_PAGAMENTO_PRE_PAGA.
             Example: 6272.
    """

    brand_name: str
    company_cnpj: str
    type_: EnumAccountType
    compe_code: str
    number: str
    check_digit: str
    account_id: str
    branch_code: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        brand_name = self.brand_name

        company_cnpj = self.company_cnpj

        type_ = self.type_.value

        compe_code = self.compe_code

        number = self.number

        check_digit = self.check_digit

        account_id = self.account_id

        branch_code = self.branch_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "brandName": brand_name,
                "companyCnpj": company_cnpj,
                "type": type_,
                "compeCode": compe_code,
                "number": number,
                "checkDigit": check_digit,
                "accountId": account_id,
            }
        )
        if branch_code is not UNSET:
            field_dict["branchCode"] = branch_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        brand_name = d.pop("brandName")

        company_cnpj = d.pop("companyCnpj")

        type_ = EnumAccountType(d.pop("type"))

        compe_code = d.pop("compeCode")

        number = d.pop("number")

        check_digit = d.pop("checkDigit")

        account_id = d.pop("accountId")

        branch_code = d.pop("branchCode", UNSET)

        account_data = cls(
            brand_name=brand_name,
            company_cnpj=company_cnpj,
            type_=type_,
            compe_code=compe_code,
            number=number,
            check_digit=check_digit,
            account_id=account_id,
            branch_code=branch_code,
        )

        account_data.additional_properties = d
        return account_data

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
