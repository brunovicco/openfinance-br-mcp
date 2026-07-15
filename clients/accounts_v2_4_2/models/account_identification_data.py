"""Accounts API model: Conjunto dos atributos que caracterizam as Contas de: depósito à vista, poupança e de pagamento pré-paga"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.accounts_v2_4_2.models.enum_account_sub_type import EnumAccountSubType
from clients.accounts_v2_4_2.models.enum_account_type import EnumAccountType
from clients.accounts_v2_4_2.types import UNSET, Unset

T = TypeVar("T", bound="AccountIdentificationData")


@_attrs_define
class AccountIdentificationData:
    """Conjunto dos atributos que caracterizam as Contas de: depósito à vista, poupança e de pagamento pré-paga

    Attributes:
        compe_code (str): Código identificador atribuído pelo Banco Central do Brasil às instituições participantes do
            STR (Sistema de Transferência de reservas). O número-código substituiu o antigo código COMPE. Todos os
            participantes do STR, exceto as Infraestruturas do Mercado Financeiro (IMF) e a Secretaria do Tesouro Nacional,
            possuem um número-código independentemente de participarem da Centralizadora da Compensação de Cheques (Compe).
            Example: 001.
        number (str): Número da conta
             Example: 24550245.
        check_digit (str): Dígito da conta
             Example: 4.
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
        subtype (EnumAccountSubType): Subtipo de conta (vide Enum):
            Conta individual - possui um único titular
            Conta conjunta simples - onde as movimentações financeiras só podem serem realizadas mediante autorização de
            TODOS os correntistas da conta.
            Conta conjunta solidária - é a modalidade cujos titulares podem realizar movimentações de forma isolada, isto é,
            sem que seja necessária a autorização dos demais titulares
             Example: INDIVIDUAL.
        currency (str): Moeda referente ao valor da transação, segundo modelo ISO-4217. p.ex. 'BRL'
            Todos os saldos informados estão representados com a moeda vigente do Brasil
             Example: BRL.
        branch_code (str | Unset): Código da Agência detentora da conta. (Agência é a dependência destinada ao
            atendimento aos clientes, ao público em geral e aos associados de cooperativas de crédito, no exercício de
            atividades da instituição, não podendo ser móvel ou transitória)

            [Restrição] Obrigatoriamente deve ser preenchido quando o campo "type" for diferente de conta pré-paga.
             Example: 6272.
    """

    compe_code: str
    number: str
    check_digit: str
    type_: EnumAccountType
    subtype: EnumAccountSubType
    currency: str
    branch_code: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        compe_code = self.compe_code

        number = self.number

        check_digit = self.check_digit

        type_ = self.type_.value

        subtype = self.subtype.value

        currency = self.currency

        branch_code = self.branch_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "compeCode": compe_code,
                "number": number,
                "checkDigit": check_digit,
                "type": type_,
                "subtype": subtype,
                "currency": currency,
            }
        )
        if branch_code is not UNSET:
            field_dict["branchCode"] = branch_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        compe_code = d.pop("compeCode")

        number = d.pop("number")

        check_digit = d.pop("checkDigit")

        type_ = EnumAccountType(d.pop("type"))

        subtype = EnumAccountSubType(d.pop("subtype"))

        currency = d.pop("currency")

        branch_code = d.pop("branchCode", UNSET)

        account_identification_data = cls(
            compe_code=compe_code,
            number=number,
            check_digit=check_digit,
            type_=type_,
            subtype=subtype,
            currency=currency,
            branch_code=branch_code,
        )

        account_identification_data.additional_properties = d
        return account_identification_data

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
