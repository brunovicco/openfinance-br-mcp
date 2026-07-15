"""Treasure Titles API model: Lista de títulos de tesouro direto mantidos pelo cliente na instituição transmissora e para as quais ele tenha"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ResponseTreasureTitlesListProductData")


@_attrs_define
class ResponseTreasureTitlesListProductData:
    """Lista de títulos de tesouro direto mantidos pelo cliente na instituição transmissora e para as quais ele tenha
    fornecido consentimento

        Attributes:
            brand_name (str): Nome da Marca reportada pelo participante no Open Finance.
                Recomenda-se utilizar, sempre que possível, o mesmo nome de marca atribuído no
                campo do diretório Customer Friendly Server Name (Authorisation Server).
                 Example: Organização A.
            company_cnpj (str): Registro completo do CNPJ da instituição responsável pelo Cadastro - o CNPJ corresponde a
                representação alfanumérica da inscrição no Cadastro de Pessoa Jurídica. Deve-se ter apenas os caracteres do
                CNPJ, sem máscara.
                 Example: 21128159000166.
            investment_id (str): Identifica de forma única o relacionamento do cliente com o
                produto, mantendo as regras de imutabilidade dentro da instituição
                transmissora.
                 Example: 92792126019929200000000000000000000000000.
    """

    brand_name: str
    company_cnpj: str
    investment_id: str

    def to_dict(self) -> dict[str, Any]:
        brand_name = self.brand_name

        company_cnpj = self.company_cnpj

        investment_id = self.investment_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "brandName": brand_name,
                "companyCnpj": company_cnpj,
                "investmentId": investment_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        brand_name = d.pop("brandName")

        company_cnpj = d.pop("companyCnpj")

        investment_id = d.pop("investmentId")

        response_treasure_titles_list_product_data = cls(
            brand_name=brand_name,
            company_cnpj=company_cnpj,
            investment_id=investment_id,
        )

        return response_treasure_titles_list_product_data
