"""Payments API model: Objeto contendo dados de pagamento para consentimento."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from clients.payments_v4_0_0.models.enum_payment_type import EnumPaymentType
from clients.payments_v4_0_0.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.payments_v4_0_0.models.details import Details
    from clients.payments_v4_0_0.models.schedule_custom import ScheduleCustom
    from clients.payments_v4_0_0.models.schedule_daily import ScheduleDaily
    from clients.payments_v4_0_0.models.schedule_monthly import ScheduleMonthly
    from clients.payments_v4_0_0.models.schedule_single import ScheduleSingle
    from clients.payments_v4_0_0.models.schedule_weekly import ScheduleWeekly


T = TypeVar("T", bound="ResponseCreatePaymentConsentDataPayment")


@_attrs_define
class ResponseCreatePaymentConsentDataPayment:
    """Objeto contendo dados de pagamento para consentimento.

    Attributes:
        type_ (EnumPaymentType): Este campo define o tipo de pagamento que será iniciado após a autorização do
            consentimento.
             Example: PIX.
        currency (str): Código da moeda nacional segundo modelo ISO-4217, ou seja, 'BRL'.
            Todos os valores monetários informados estão representados com a moeda vigente do Brasil.
             Example: BRL.
        amount (str): Valor da transação com 2 casas decimais. O valor deve ser o mesmo enviado no consentimento.

            Para QR Code estático com valor pré-determinado no QR Code ou para QR Code dinâmico com indicação de que o valor
            não pode ser alterado: O campo amount deve ser preenchido com o valor estabelecido no QR Code.
            Caso seja preenchido com valor divergente do QR Code, deve ser retornado um erro HTTP Status 422.
             Example: 100000.12.
        details (Details): Objeto contendo os detalhes do pagamento.
        schedule (ScheduleCustom | ScheduleDaily | ScheduleMonthly | ScheduleSingle | ScheduleWeekly | Unset):
            [Restrição] Mutuamente excludente com o campo date.
            Este campo é obrigatório no caso de agendamento.
            Neste caso, o campo date não deverá ser informado.
            O prazo máximo para o consentimento deverá ser de dois anos, contando a partir da data de criação do
            consentimento retornada na criação do mesmo (campo /data/creationDateTime).
            Agendamento de pagamento único deve utilizar exclusivamente o objeto "single".
        date (datetime.date | Unset): [Restrição] Mutuamente excludente com o objeto schedule.

            Este campo é obrigatório no caso de pagamento único.

            Neste caso, o objeto schedule não deve ser informado.
             Example: 2021-01-01.
        ibge_town_code (str | Unset): O campo ibgetowncode no arranjo PIX, tem o mesmo comportamento que o campo codMun
            descrito no item 1.6.6 do manual do PIX, conforme segue:

            1. Caso a informação referente ao município não seja enviada; o PSP do recebedor assumirá que não existem
            feriados estaduais e municipais no período em questão;
             Example: 5300108.
    """

    type_: EnumPaymentType
    currency: str
    amount: str
    details: 'Details'
    schedule: (
        'ScheduleCustom | ScheduleDaily | ScheduleMonthly | ScheduleSingle | ScheduleWeekly | Unset'
    ) = UNSET
    date: datetime.date | Unset = UNSET
    ibge_town_code: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from clients.payments_v4_0_0.models.schedule_daily import ScheduleDaily
        from clients.payments_v4_0_0.models.schedule_monthly import ScheduleMonthly
        from clients.payments_v4_0_0.models.schedule_single import ScheduleSingle
        from clients.payments_v4_0_0.models.schedule_weekly import ScheduleWeekly

        type_ = self.type_.value

        currency = self.currency

        amount = self.amount

        details = self.details.to_dict()

        schedule: dict[str, Any] | Unset
        if isinstance(self.schedule, Unset):
            schedule = UNSET
        elif isinstance(self.schedule, ScheduleSingle):
            schedule = self.schedule.to_dict()
        elif isinstance(self.schedule, ScheduleDaily):
            schedule = self.schedule.to_dict()
        elif isinstance(self.schedule, ScheduleWeekly):
            schedule = self.schedule.to_dict()
        elif isinstance(self.schedule, ScheduleMonthly):
            schedule = self.schedule.to_dict()
        else:
            schedule = self.schedule.to_dict()

        date: str | Unset = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        ibge_town_code = self.ibge_town_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "currency": currency,
                "amount": amount,
                "details": details,
            }
        )
        if schedule is not UNSET:
            field_dict["schedule"] = schedule
        if date is not UNSET:
            field_dict["date"] = date
        if ibge_town_code is not UNSET:
            field_dict["ibgeTownCode"] = ibge_town_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.payments_v4_0_0.models.details import Details
        from clients.payments_v4_0_0.models.schedule_custom import ScheduleCustom
        from clients.payments_v4_0_0.models.schedule_daily import ScheduleDaily
        from clients.payments_v4_0_0.models.schedule_monthly import ScheduleMonthly
        from clients.payments_v4_0_0.models.schedule_single import ScheduleSingle
        from clients.payments_v4_0_0.models.schedule_weekly import ScheduleWeekly

        d = dict(src_dict)
        type_ = EnumPaymentType(d.pop("type"))

        currency = d.pop("currency")

        amount = d.pop("amount")

        details = Details.from_dict(d.pop("details"))

        def _parse_schedule(
            data: object,
        ) -> (
            'ScheduleCustom | ScheduleDaily | ScheduleMonthly | ScheduleSingle | ScheduleWeekly | Unset'
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schedule_type_0 = ScheduleSingle.from_dict(data)

                return componentsschemas_schedule_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schedule_type_1 = ScheduleDaily.from_dict(data)

                return componentsschemas_schedule_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schedule_type_2 = ScheduleWeekly.from_dict(data)

                return componentsschemas_schedule_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schedule_type_3 = ScheduleMonthly.from_dict(data)

                return componentsschemas_schedule_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_schedule_type_4 = ScheduleCustom.from_dict(data)

            return componentsschemas_schedule_type_4

        schedule = _parse_schedule(d.pop("schedule", UNSET))

        _date = d.pop("date", UNSET)
        date: datetime.date | Unset
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date).date()

        ibge_town_code = d.pop("ibgeTownCode", UNSET)

        response_create_payment_consent_data_payment = cls(
            type_=type_,
            currency=currency,
            amount=amount,
            details=details,
            schedule=schedule,
            date=date,
            ibge_town_code=ibge_town_code,
        )

        response_create_payment_consent_data_payment.additional_properties = d
        return response_create_payment_consent_data_payment

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
