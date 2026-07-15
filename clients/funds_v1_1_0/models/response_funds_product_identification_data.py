"""Funds API model: Informações do produto de fundo de investimento a que se refere investmentId."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from clients.funds_v1_1_0.models.response_funds_product_identification_data_anbima_category import (
    ResponseFundsProductIdentificationDataAnbimaCategory,
)
from clients.funds_v1_1_0.types import UNSET, Unset

T = TypeVar("T", bound="ResponseFundsProductIdentificationData")


@_attrs_define
class ResponseFundsProductIdentificationData:
    """Informações do produto de fundo de investimento a que se refere investmentId.

    Attributes:
        name (str): Nome oficial do fundo de investimento conforme exibido para os clientes nos canais eletrônicos.
            Example: CONSTELLATION MASTER FIA.
        cnpj_number (str): CNPJ do fundo de investimento. Example: 11225860000140.
        isin_code (str | Unset): Código universal que identifica cada valor mobiliário ou instrumento financeiro,
            conforme Norma ISO 6166.

            DEFINIÇÃO: O ISIN (International Securities Identification Number) é um código que identifica um valor
            mobiliário, conforme a norma ISO 6166.

            ESTRUTURA: O ISIN é um código alfanumérico que possui 12 caracteres com a seguinte estrutura:
            - Um prefixo, composto de 2 caracteres alfa, que identifica o código do país (Norma ISO 3166);
            - O número básico, composto de 9 caracteres alfabéticos ou numéricos em sua extensão;
            - Um dígito numérico de controle.
             Example: BRCST4CTF001.
        anbima_category (ResponseFundsProductIdentificationDataAnbimaCategory | Unset): Conforme classificação ANBIMA,
            que segue a deliberação 77 da ANBIMA.

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

    name: str
    cnpj_number: str
    isin_code: str | Unset = UNSET
    anbima_category: ResponseFundsProductIdentificationDataAnbimaCategory | Unset = (
        UNSET
    )
    anbima_class: str | Unset = UNSET
    anbima_subclass: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        cnpj_number = self.cnpj_number

        isin_code = self.isin_code

        anbima_category: str | Unset = UNSET
        if not isinstance(self.anbima_category, Unset):
            anbima_category = self.anbima_category.value

        anbima_class = self.anbima_class

        anbima_subclass = self.anbima_subclass

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "cnpjNumber": cnpj_number,
            }
        )
        if isin_code is not UNSET:
            field_dict["isinCode"] = isin_code
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
        name = d.pop("name")

        cnpj_number = d.pop("cnpjNumber")

        isin_code = d.pop("isinCode", UNSET)

        _anbima_category = d.pop("anbimaCategory", UNSET)
        anbima_category: ResponseFundsProductIdentificationDataAnbimaCategory | Unset
        if isinstance(_anbima_category, Unset):
            anbima_category = UNSET
        else:
            anbima_category = ResponseFundsProductIdentificationDataAnbimaCategory(
                _anbima_category
            )

        anbima_class = d.pop("anbimaClass", UNSET)

        anbima_subclass = d.pop("anbimaSubclass", UNSET)

        response_funds_product_identification_data = cls(
            name=name,
            cnpj_number=cnpj_number,
            isin_code=isin_code,
            anbima_category=anbima_category,
            anbima_class=anbima_class,
            anbima_subclass=anbima_subclass,
        )

        return response_funds_product_identification_data
