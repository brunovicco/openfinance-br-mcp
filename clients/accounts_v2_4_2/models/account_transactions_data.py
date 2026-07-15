"""AccountTransactionsData: a data model of the Accounts API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.accounts_v2_4_2.models.enum_completed_authorised_payment_indicator import (
    EnumCompletedAuthorisedPaymentIndicator,
)
from clients.accounts_v2_4_2.models.enum_credit_debit_indicator import EnumCreditDebitIndicator
from clients.accounts_v2_4_2.models.enum_partie_person_type import EnumPartiePersonType
from clients.accounts_v2_4_2.models.enum_transaction_types import EnumTransactionTypes
from clients.accounts_v2_4_2.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.accounts_v2_4_2.models.account_transactions_data_amount import AccountTransactionsDataAmount


T = TypeVar("T", bound="AccountTransactionsData")


@_attrs_define
class AccountTransactionsData:
    """
    Attributes:
        transaction_id (str): Código ou identificador único prestado pela instituição que mantém a conta para
            representar a transação individual.
            O ideal é que o `transactionId` seja imutável.
            No entanto, o `transactionId` deve obedecer, no mínimo, as regras de imutabilidade propostas conforme tabela
            “Data de imutabilidade por tipo de transação” presente nas orientações desta API.
             Example: TXpRMU9UQTROMWhZV2xSU1FUazJSMDl.
        completed_authorised_payment_type (EnumCompletedAuthorisedPaymentIndicator): Indicador da transação:
              - Transação efetivada: a transação atinge esse status quando o `transactionId` torna-se imutável;
              - Lançamento futuro: a transação será efetivada em momento futuro, ou seja, o `transactionId` pode mudar;
              - Transação processando: a transação está em processamento, ou seja, o `transactionId` pode mudar.
             Example: TRANSACAO_EFETIVADA.
        credit_debit_type (EnumCreditDebitIndicator): Indicador do tipo de lançamento:
            Débito (no extrato) Em um extrato bancário, os débitos, marcados com a letra “D” ao lado do valor registrado,
            informam as saídas de dinheiro na conta-corrente.
            Crédito (no extrato) Em um extrato bancário, os créditos, marcados com a letra “C” ao lado do valor registrado,
            informam as entradas de dinheiro na conta-corrente.
             Example: DEBITO.
        transaction_name (str): Literal usada na instituição financeira para identificar a transação.
            A informação apresentada precisa ser a mesma utilizada nos canais digitais da instituição (assim como o
            histórico de transações apresentado na tela do aplicativo ou do navegador).
            Caso a instituição possua mais de um canal digital, a informação compartilhada deve ser a do canal que apresenta
            a descrição mais completa possível da transação.
            Em casos onde a descrição da transação é apresentada com múltiplas linhas, todas as linhas devem ser enviadas
            (concatenadas) neste atributo, não sendo obrigatória a concatenação das informações já enviadas em outros
            atributos (ex: valor, data) do mesmo endpoint.
            Adicionalmente, o Banco Central pode determinar o formato de compartilhamento a ser adotado por uma instituição
            participante específica.
             Example: Transferencia Enviada Lima Santos.
        type_ (EnumTransactionTypes): O campo deve classificar a transação em um dos tipos descritos.
            O transmissor deve classificar as transações disponíveis associando-a a um dos itens do Enum listado neste
            campo.
            A opção OUTROS só deve ser utilizada para os casos em que de fato a transação compartilhada não possa ser
            classificada como um dos itens deste Enum.
            Por exemplo no caso de recebimento de pensão alimentícia.
             Example: PIX.
        transaction_amount (AccountTransactionsDataAmount): Valor da transação. Expresso em valor monetário com no
            mínimo 2 casas e no máximo 4 casas decimais.
        transaction_date_time (str): Data e hora original da transação.
             Example: 2016-01-29T12:29:03.374Z.
        partie_cnpj_cpf (str | Unset): Identificação da pessoa envolvida na transação: pagador ou recebedor (Preencher
            com o CPF ou CNPJ, sem formatação). Com a IN BCB nº 371, a partir de 02/05/23, o envio das informações de
            identificação de contraparte tornou-se obrigatória para transações de pagamento. Para maiores detalhes, favor
            consultar a página `Orientações - Contas`.

            [Restrição] Quando o "type“ for preenchido com valor FOLHA_PAGAMENTO e a transmissora for a responsável pelo
            pagamento de salário (banco-folha), o partieCnpjCpf informado deve ser do empregador relacionado.
             Example: 43908445778.
        partie_person_type (EnumPartiePersonType | Unset): Identificação do Tipo de Pessoa da pessoa envolvida na
            transação.
            Pessoa Natural - Informar CPF no campo “partieCnpjCpf”.
            Pessoa Jurídica - Informar CNPJ no campo “partieCnpjCpf”.
             Example: PESSOA_NATURAL.
        partie_compe_code (str | Unset): Código identificador atribuído pelo Banco Central do Brasil às instituições
            participantes do STR (Sistema de Transferência de reservas) referente à pessoa envolvida na transação. O número-
            código substituiu o antigo código COMPE. Todos os participantes do STR, exceto as Infraestruturas do Mercado
            Financeiro (IMF) e a Secretaria do Tesouro Nacional, possuem um número-código independentemente de participarem
            da Centralizadora da Compensação de Cheques (Compe). Example: 001.
        partie_branch_code (str | Unset): Código da Agência detentora da conta da pessoa envolvida na transação.
            (Agência é a dependência destinada ao atendimento aos clientes, ao público em geral e aos associados de
            cooperativas de crédito, no exercício de atividades da instituição, não podendo ser móvel ou transitória)
            Example: 6272.
        partie_number (str | Unset): Número da conta da pessoa envolvida na transação Example: 67890854360.
        partie_check_digit (str | Unset): Dígito da conta da pessoa envolvida na transação Example: 4.
    """

    transaction_id: str
    completed_authorised_payment_type: EnumCompletedAuthorisedPaymentIndicator
    credit_debit_type: EnumCreditDebitIndicator
    transaction_name: str
    type_: EnumTransactionTypes
    transaction_amount: 'AccountTransactionsDataAmount'
    transaction_date_time: str
    partie_cnpj_cpf: str | Unset = UNSET
    partie_person_type: EnumPartiePersonType | Unset = UNSET
    partie_compe_code: str | Unset = UNSET
    partie_branch_code: str | Unset = UNSET
    partie_number: str | Unset = UNSET
    partie_check_digit: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        transaction_id = self.transaction_id

        completed_authorised_payment_type = self.completed_authorised_payment_type.value

        credit_debit_type = self.credit_debit_type.value

        transaction_name = self.transaction_name

        type_ = self.type_.value

        transaction_amount = self.transaction_amount.to_dict()

        transaction_date_time = self.transaction_date_time

        partie_cnpj_cpf = self.partie_cnpj_cpf

        partie_person_type: str | Unset = UNSET
        if not isinstance(self.partie_person_type, Unset):
            partie_person_type = self.partie_person_type.value

        partie_compe_code = self.partie_compe_code

        partie_branch_code = self.partie_branch_code

        partie_number = self.partie_number

        partie_check_digit = self.partie_check_digit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transactionId": transaction_id,
                "completedAuthorisedPaymentType": completed_authorised_payment_type,
                "creditDebitType": credit_debit_type,
                "transactionName": transaction_name,
                "type": type_,
                "transactionAmount": transaction_amount,
                "transactionDateTime": transaction_date_time,
            }
        )
        if partie_cnpj_cpf is not UNSET:
            field_dict["partieCnpjCpf"] = partie_cnpj_cpf
        if partie_person_type is not UNSET:
            field_dict["partiePersonType"] = partie_person_type
        if partie_compe_code is not UNSET:
            field_dict["partieCompeCode"] = partie_compe_code
        if partie_branch_code is not UNSET:
            field_dict["partieBranchCode"] = partie_branch_code
        if partie_number is not UNSET:
            field_dict["partieNumber"] = partie_number
        if partie_check_digit is not UNSET:
            field_dict["partieCheckDigit"] = partie_check_digit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.accounts_v2_4_2.models.account_transactions_data_amount import (
            AccountTransactionsDataAmount,
        )

        d = dict(src_dict)
        transaction_id = d.pop("transactionId")

        completed_authorised_payment_type = EnumCompletedAuthorisedPaymentIndicator(
            d.pop("completedAuthorisedPaymentType")
        )

        credit_debit_type = EnumCreditDebitIndicator(d.pop("creditDebitType"))

        transaction_name = d.pop("transactionName")

        type_ = EnumTransactionTypes(d.pop("type"))

        transaction_amount = AccountTransactionsDataAmount.from_dict(
            d.pop("transactionAmount")
        )

        transaction_date_time = d.pop("transactionDateTime")

        partie_cnpj_cpf = d.pop("partieCnpjCpf", UNSET)

        _partie_person_type = d.pop("partiePersonType", UNSET)
        partie_person_type: EnumPartiePersonType | Unset
        if isinstance(_partie_person_type, Unset):
            partie_person_type = UNSET
        else:
            partie_person_type = EnumPartiePersonType(_partie_person_type)

        partie_compe_code = d.pop("partieCompeCode", UNSET)

        partie_branch_code = d.pop("partieBranchCode", UNSET)

        partie_number = d.pop("partieNumber", UNSET)

        partie_check_digit = d.pop("partieCheckDigit", UNSET)

        account_transactions_data = cls(
            transaction_id=transaction_id,
            completed_authorised_payment_type=completed_authorised_payment_type,
            credit_debit_type=credit_debit_type,
            transaction_name=transaction_name,
            type_=type_,
            transaction_amount=transaction_amount,
            transaction_date_time=transaction_date_time,
            partie_cnpj_cpf=partie_cnpj_cpf,
            partie_person_type=partie_person_type,
            partie_compe_code=partie_compe_code,
            partie_branch_code=partie_branch_code,
            partie_number=partie_number,
            partie_check_digit=partie_check_digit,
        )

        account_transactions_data.additional_properties = d
        return account_transactions_data

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
