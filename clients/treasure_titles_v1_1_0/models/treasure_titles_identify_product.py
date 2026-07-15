"""TreasureTitlesIdentifyProduct: a data model of the Treasure Titles API (Open Finance Brasil), per the OpenAPI spec's schema for it."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.treasure_titles_v1_1_0.models.treasure_titles_voucher_payment_indicator import (
    TreasureTitlesVoucherPaymentIndicator,
)
from clients.treasure_titles_v1_1_0.models.treasure_titles_voucher_payment_periodicity import (
    TreasureTitlesVoucherPaymentPeriodicity,
)
from clients.treasure_titles_v1_1_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.treasure_titles_v1_1_0.models.treasure_titles_remuneration import TreasureTitlesRemuneration


T = TypeVar("T", bound="TreasureTitlesIdentifyProduct")


@_attrs_define
class TreasureTitlesIdentifyProduct:
    """
    Attributes:
        isin_code (str): Código ISIN da emissão, Código ISIN do produto, Código da emissora
            : código universal que identifica cada valor mobiliário ou instrumento
            financeiro, conforme Norma ISO 6166.
             Example: BRCST4CTF001.
        product_name (str): Nome do título em questão, conforme listado no site do Tesouro Direto
            [https://www.tesourodireto.com.br](https://www.tesourodireto.com.br) Example: Tesouro Selic 2025.
        remuneration (TreasureTitlesRemuneration): Objeto para detalhamento de remuneração do titulo.
        due_date (datetime.date): Data de vencimento do título. Example: 2018-02-15.
        purchase_date (datetime.date): Data de aquisição do cliente. Example: 2018-02-15.
        voucher_payment_indicator (TreasureTitlesVoucherPaymentIndicator): Indicativo se há pagamento de cupom (Sim ou
            não). Example: SIM.
        voucher_payment_periodicity (TreasureTitlesVoucherPaymentPeriodicity | Unset): Em caso de haver pagamento de
            cupom, descrever a periodicidade
            (mensal, trimestral, semestral, anual, irregular e outros)

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'voucherPaymentIndicator' for
            preenchido com o valor 'SIM'.
             Example: MENSAL.
        voucher_payment_periodicity_additional_info (str | Unset): Informações adicionais da periodicidade de pagamento
            de cupom.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'voucherPaymentPeriodicity'
            for preenchido com o valor 'OUTROS'.
             Example: Diária.
    """

    isin_code: str
    product_name: str
    remuneration: 'TreasureTitlesRemuneration'
    due_date: datetime.date
    purchase_date: datetime.date
    voucher_payment_indicator: TreasureTitlesVoucherPaymentIndicator
    voucher_payment_periodicity: TreasureTitlesVoucherPaymentPeriodicity | Unset = UNSET
    voucher_payment_periodicity_additional_info: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        isin_code = self.isin_code

        product_name = self.product_name

        remuneration = self.remuneration.to_dict()

        due_date = self.due_date.isoformat()

        purchase_date = self.purchase_date.isoformat()

        voucher_payment_indicator = self.voucher_payment_indicator.value

        voucher_payment_periodicity: str | Unset = UNSET
        if not isinstance(self.voucher_payment_periodicity, Unset):
            voucher_payment_periodicity = self.voucher_payment_periodicity.value

        voucher_payment_periodicity_additional_info = (
            self.voucher_payment_periodicity_additional_info
        )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isinCode": isin_code,
                "productName": product_name,
                "remuneration": remuneration,
                "dueDate": due_date,
                "purchaseDate": purchase_date,
                "voucherPaymentIndicator": voucher_payment_indicator,
            }
        )
        if voucher_payment_periodicity is not UNSET:
            field_dict["voucherPaymentPeriodicity"] = voucher_payment_periodicity
        if voucher_payment_periodicity_additional_info is not UNSET:
            field_dict["voucherPaymentPeriodicityAdditionalInfo"] = (
                voucher_payment_periodicity_additional_info
            )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.treasure_titles_v1_1_0.models.treasure_titles_remuneration import TreasureTitlesRemuneration

        d = dict(src_dict)
        isin_code = d.pop("isinCode")

        product_name = d.pop("productName")

        remuneration = TreasureTitlesRemuneration.from_dict(d.pop("remuneration"))

        due_date = isoparse(d.pop("dueDate")).date()

        purchase_date = isoparse(d.pop("purchaseDate")).date()

        voucher_payment_indicator = TreasureTitlesVoucherPaymentIndicator(
            d.pop("voucherPaymentIndicator")
        )

        _voucher_payment_periodicity = d.pop("voucherPaymentPeriodicity", UNSET)
        voucher_payment_periodicity: TreasureTitlesVoucherPaymentPeriodicity | Unset
        if isinstance(_voucher_payment_periodicity, Unset):
            voucher_payment_periodicity = UNSET
        else:
            voucher_payment_periodicity = TreasureTitlesVoucherPaymentPeriodicity(
                _voucher_payment_periodicity
            )

        voucher_payment_periodicity_additional_info = d.pop(
            "voucherPaymentPeriodicityAdditionalInfo", UNSET
        )

        treasure_titles_identify_product = cls(
            isin_code=isin_code,
            product_name=product_name,
            remuneration=remuneration,
            due_date=due_date,
            purchase_date=purchase_date,
            voucher_payment_indicator=voucher_payment_indicator,
            voucher_payment_periodicity=voucher_payment_periodicity,
            voucher_payment_periodicity_additional_info=voucher_payment_periodicity_additional_info,
        )

        treasure_titles_identify_product.additional_properties = d
        return treasure_titles_identify_product

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
