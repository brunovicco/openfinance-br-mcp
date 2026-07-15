"""IdentifyProduct: a data model of the Bank Fixed Incomes API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from clients.bank_fixed_incomes_v1_1_0.models.enum_investment_type import EnumInvestmentType
from clients.bank_fixed_incomes_v1_1_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.bank_fixed_incomes_v1_1_0.models.identify_product_issue_unit_price import IdentifyProductIssueUnitPrice
    from clients.bank_fixed_incomes_v1_1_0.models.remuneration import Remuneration


T = TypeVar("T", bound="IdentifyProduct")


@_attrs_define
class IdentifyProduct:
    """
    Attributes:
        issuer_institution_cnpj_number (str): CNPJ da instituição emissora. Example: 11225860000140.
        investment_type (EnumInvestmentType): Especificação do ativo em questão (CDB, RDB, LCI ou LCA) Example: CDB.
        remuneration (Remuneration): Objeto para detalhamento de remuneração do titulo.
        issue_unit_price (IdentifyProductIssueUnitPrice): Preço unitário de emissão do título.
        due_date (datetime.date): Data de vencimento do título. Example: 2018-02-15.
        issue_date (datetime.date): Data de emissão do título. Example: 2018-02-16.
        purchase_date (datetime.date): Data de aquisição do cliente. Example: 2018-02-15.
        grace_period_date (datetime.date): Data até a qual o cliente não poderá resgatar antecipadamente seu
            investimento. Example: 2018-02-16.
        isin_code (str | Unset): Código ISIN da emissão, Código ISIN do produto, Código da emissora (campo opcional):
            código universal que identifica cada valor mobiliário ou instrumento financeiro, conforme Norma ISO 6166
             Example: BRCST4CTF001.
        clearing_code (str | Unset): Código de registro do ativo na clearing. Example: CDB421GPXXX.
    """

    issuer_institution_cnpj_number: str
    investment_type: EnumInvestmentType
    remuneration: 'Remuneration'
    issue_unit_price: 'IdentifyProductIssueUnitPrice'
    due_date: datetime.date
    issue_date: datetime.date
    purchase_date: datetime.date
    grace_period_date: datetime.date
    isin_code: str | Unset = UNSET
    clearing_code: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        issuer_institution_cnpj_number = self.issuer_institution_cnpj_number

        investment_type = self.investment_type.value

        remuneration = self.remuneration.to_dict()

        issue_unit_price = self.issue_unit_price.to_dict()

        due_date = self.due_date.isoformat()

        issue_date = self.issue_date.isoformat()

        purchase_date = self.purchase_date.isoformat()

        grace_period_date = self.grace_period_date.isoformat()

        isin_code = self.isin_code

        clearing_code = self.clearing_code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "issuerInstitutionCnpjNumber": issuer_institution_cnpj_number,
                "investmentType": investment_type,
                "remuneration": remuneration,
                "issueUnitPrice": issue_unit_price,
                "dueDate": due_date,
                "issueDate": issue_date,
                "purchaseDate": purchase_date,
                "gracePeriodDate": grace_period_date,
            }
        )
        if isin_code is not UNSET:
            field_dict["isinCode"] = isin_code
        if clearing_code is not UNSET:
            field_dict["clearingCode"] = clearing_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.bank_fixed_incomes_v1_1_0.models.identify_product_issue_unit_price import (
            IdentifyProductIssueUnitPrice,
        )
        from clients.bank_fixed_incomes_v1_1_0.models.remuneration import Remuneration

        d = dict(src_dict)
        issuer_institution_cnpj_number = d.pop("issuerInstitutionCnpjNumber")

        investment_type = EnumInvestmentType(d.pop("investmentType"))

        remuneration = Remuneration.from_dict(d.pop("remuneration"))

        issue_unit_price = IdentifyProductIssueUnitPrice.from_dict(
            d.pop("issueUnitPrice")
        )

        due_date = isoparse(d.pop("dueDate")).date()

        issue_date = isoparse(d.pop("issueDate")).date()

        purchase_date = isoparse(d.pop("purchaseDate")).date()

        grace_period_date = isoparse(d.pop("gracePeriodDate")).date()

        isin_code = d.pop("isinCode", UNSET)

        clearing_code = d.pop("clearingCode", UNSET)

        identify_product = cls(
            issuer_institution_cnpj_number=issuer_institution_cnpj_number,
            investment_type=investment_type,
            remuneration=remuneration,
            issue_unit_price=issue_unit_price,
            due_date=due_date,
            issue_date=issue_date,
            purchase_date=purchase_date,
            grace_period_date=grace_period_date,
            isin_code=isin_code,
            clearing_code=clearing_code,
        )

        return identify_product
