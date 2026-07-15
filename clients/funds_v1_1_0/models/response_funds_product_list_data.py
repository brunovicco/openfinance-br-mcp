"""Funds API model: Lista de fundos de investimento mantidos pelo cliente na instituição transmissora e para as quais ele tenha"""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from clients.funds_v1_1_0.models.response_funds_product_list_data_anbima_category import (
    ResponseFundsProductListDataAnbimaCategory,
)
from clients.funds_v1_1_0.types import UNSET, Unset

T = TypeVar("T", bound="ResponseFundsProductListData")


@_attrs_define
class ResponseFundsProductListData:
    """Lista de fundos de investimento mantidos pelo cliente na instituição transmissora e para as quais ele tenha
    fornecido consentimento.

        Attributes:
            brand_name (str): Nome da Marca reportada pelo participante no Open Finance. Recomenda-se utilizar, sempre que
                possível, o mesmo nome de marca atribuído no campo do diretório Customer Friendly Server Name (Authorisation
                Server). Example: Organização A.
            company_cnpj (str): Registro completo do CNPJ da instituição responsável pelo Cadastro - o CNPJ corresponde a
                representação alfanumérica da inscrição no Cadastro de Pessoa Jurídica. Deve-se ter apenas os caracteres do
                CNPJ, sem máscara. Example: 21128159000166.
            investment_id (str): Identifica de forma única o relacionamento do cliente com o produto, mantendo as regras de
                imutabilidade dentro da instituição transmissora. Nos casos em que o cliente, após completar 12 meses da última
                movimentação e com quantidade de ativos zerada (cliente não tem mais posse do produto sob custódia da
                transmissora), compre novamente o ativo que já investiu em períodos passados, manter o mesmo investmentId
                anteriormente utilizado. Example: 92792126019929200000000000000000000000000.
            anbima_category (ResponseFundsProductListDataAnbimaCategory | Unset): Conforme classificação ANBIMA, que segue a
                deliberação 77 da ANBIMA.

                – Renda Fixa

                – Ações

                – Multimercado

                – Cambial

                https://www.anbima.com.br/data/files/5A/44/2C/B7/8411B510CD3B4DA568A80AC2/DeliberacaoN77-Diretriz-de-
                Classificacao-de-Fundos.pdf
                 Example: RENDA_FIXA.
            anbima_class (str | Unset): Campo necessário para aderência a Resolução CVM175. Aguardando definições de
                mercado. Deve se tratar de campo do tipo enum.
            anbima_subclass (str | Unset): Campo necessário para aderência a Resolução CVM175. Aguardando definições de
                mercado. Deve se tratar de campo do tipo enum.
    """

    brand_name: str
    company_cnpj: str
    investment_id: str
    anbima_category: ResponseFundsProductListDataAnbimaCategory | Unset = UNSET
    anbima_class: str | Unset = UNSET
    anbima_subclass: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        brand_name = self.brand_name

        company_cnpj = self.company_cnpj

        investment_id = self.investment_id

        anbima_category: str | Unset = UNSET
        if not isinstance(self.anbima_category, Unset):
            anbima_category = self.anbima_category.value

        anbima_class = self.anbima_class

        anbima_subclass = self.anbima_subclass

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "brandName": brand_name,
                "companyCnpj": company_cnpj,
                "investmentId": investment_id,
            }
        )
        if anbima_category is not UNSET:
            field_dict["anbimaCategory"] = anbima_category
        if anbima_class is not UNSET:
            field_dict["anbimaClass"] = anbima_class
        if anbima_subclass is not UNSET:
            field_dict["anbimaSubclass"] = anbima_subclass

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        brand_name = d.pop("brandName")

        company_cnpj = d.pop("companyCnpj")

        investment_id = d.pop("investmentId")

        _anbima_category = d.pop("anbimaCategory", UNSET)
        anbima_category: ResponseFundsProductListDataAnbimaCategory | Unset
        if isinstance(_anbima_category, Unset):
            anbima_category = UNSET
        else:
            anbima_category = ResponseFundsProductListDataAnbimaCategory(
                _anbima_category
            )

        anbima_class = d.pop("anbimaClass", UNSET)

        anbima_subclass = d.pop("anbimaSubclass", UNSET)

        response_funds_product_list_data = cls(
            brand_name=brand_name,
            company_cnpj=company_cnpj,
            investment_id=investment_id,
            anbima_category=anbima_category,
            anbima_class=anbima_class,
            anbima_subclass=anbima_subclass,
        )

        return response_funds_product_list_data
