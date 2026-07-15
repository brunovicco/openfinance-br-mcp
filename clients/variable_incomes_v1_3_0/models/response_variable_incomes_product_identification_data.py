"""ResponseVariableIncomesProductIdentificationData: a data model of the Variable Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from clients.variable_incomes_v1_3_0.types import UNSET, Unset

T = TypeVar("T", bound="ResponseVariableIncomesProductIdentificationData")


@_attrs_define
class ResponseVariableIncomesProductIdentificationData:
    """
    Attributes:
        isin_code (str): Código ISIN da emissão, Código ISIN do produto, Código da emissora: código universal que
            identifica cada valor mobiliário ou instrumento financeiro, conforme Norma ISO 6166.
             Example: BRCST4CTF001.
        ticker (str): Código de negociação para identificação de ativos negociados em bolsa. Example: PETR4.
        issuer_institution_cnpj_number (str | Unset): CNPJ da instituição emissora. Caso a transmissora possua a
            informação o envio deste campo é obrigatório. Example: 11225860000140.
    """

    isin_code: str
    ticker: str
    issuer_institution_cnpj_number: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        isin_code = self.isin_code

        ticker = self.ticker

        issuer_institution_cnpj_number = self.issuer_institution_cnpj_number

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "isinCode": isin_code,
                "ticker": ticker,
            }
        )
        if issuer_institution_cnpj_number is not UNSET:
            field_dict["issuerInstitutionCnpjNumber"] = issuer_institution_cnpj_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        isin_code = d.pop("isinCode")

        ticker = d.pop("ticker")

        issuer_institution_cnpj_number = d.pop("issuerInstitutionCnpjNumber", UNSET)

        response_variable_incomes_product_identification_data = cls(
            isin_code=isin_code,
            ticker=ticker,
            issuer_institution_cnpj_number=issuer_institution_cnpj_number,
        )

        return response_variable_incomes_product_identification_data
