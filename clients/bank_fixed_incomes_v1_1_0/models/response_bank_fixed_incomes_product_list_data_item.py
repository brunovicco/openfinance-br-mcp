"""Bank Fixed Incomes API model: Lista de títulos de renda fixa bancária mantidos pelo cliente na instituição transmissora e para as quais ele tenha"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from clients.bank_fixed_incomes_v1_1_0.models.enum_investment_type import EnumInvestmentType

T = TypeVar("T", bound="ResponseBankFixedIncomesProductListDataItem")


@_attrs_define
class ResponseBankFixedIncomesProductListDataItem:
    """Lista de títulos de renda fixa bancária mantidos pelo cliente na instituição transmissora e para as quais ele tenha
    fornecido consentimento

        Attributes:
            brand_name (str): Nome da Marca reportada pelo participante no Open Finance. Recomenda-se utilizar, sempre que
                possível, o mesmo nome de marca atribuído no campo do diretório Customer Friendly Server Name (Authorisation
                Server). Example: Organização A.
            company_cnpj (str): Registro completo do CNPJ da instituição responsável pelo Cadastro - o CNPJ corresponde a
                representação alfanumérica da inscrição no Cadastro de Pessoa Jurídica. Deve-se ter apenas os caracteres do
                CNPJ, sem máscara. Example: 21281590001660.
            investment_type (EnumInvestmentType): Especificação do ativo em questão (CDB, RDB, LCI ou LCA) Example: CDB.
            investment_id (str): Identifica de forma única  o relacionamento do cliente com o produto, mantendo as regras de
                imutabilidade dentro da instituição transmissora. Example: 92792126019929200000000000000000000000000.
    """

    brand_name: str
    company_cnpj: str
    investment_type: EnumInvestmentType
    investment_id: str

    def to_dict(self) -> dict[str, Any]:
        brand_name = self.brand_name

        company_cnpj = self.company_cnpj

        investment_type = self.investment_type.value

        investment_id = self.investment_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "brandName": brand_name,
                "companyCnpj": company_cnpj,
                "investmentType": investment_type,
                "investmentId": investment_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        brand_name = d.pop("brandName")

        company_cnpj = d.pop("companyCnpj")

        investment_type = EnumInvestmentType(d.pop("investmentType"))

        investment_id = d.pop("investmentId")

        response_bank_fixed_incomes_product_list_data_item = cls(
            brand_name=brand_name,
            company_cnpj=company_cnpj,
            investment_type=investment_type,
            investment_id=investment_id,
        )

        return response_bank_fixed_incomes_product_list_data_item
