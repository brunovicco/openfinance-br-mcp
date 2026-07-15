"""Credit Cards Accounts API model: Conjunto de informações referentes aos limites da conta de pagamento pós-paga."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.credit_cards_v2_3_1.models.credit_card_accounts_limits_data_line_name import (
    CreditCardAccountsLimitsDataLineName,
)
from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_consolidation_type import (
    EnumCreditCardAccountsConsolidationType,
)
from clients.credit_cards_v2_3_1.models.enum_credit_card_accounts_line_limit_type import (
    EnumCreditCardAccountsLineLimitType,
)
from clients.credit_cards_v2_3_1.types import UNSET, Unset

if TYPE_CHECKING:
    from clients.credit_cards_v2_3_1.models.credit_card_accounts_limits_data_customized_limit_amount import (
        CreditCardAccountsLimitsDataCustomizedLimitAmount,
    )
    from clients.credit_cards_v2_3_1.models.credit_cards_available_amount import CreditCardsAvailableAmount
    from clients.credit_cards_v2_3_1.models.credit_cards_limit_amount import CreditCardsLimitAmount
    from clients.credit_cards_v2_3_1.models.credit_cards_used_amount import CreditCardsUsedAmount


T = TypeVar("T", bound="CreditCardAccountsLimitsData")


@_attrs_define
class CreditCardAccountsLimitsData:
    """Conjunto de informações referentes aos limites da conta de pagamento pós-paga.

    Attributes:
        credit_line_limit_type (EnumCreditCardAccountsLineLimitType): Indicador do tipo de limite

            LIMITE_CREDITO_TOTAL: Limite de crédito total aplicado a conta cartão.

            LIMITE_CREDITO_MODALIDADE_OPERACAO: Limite de crédito por modalidade desse conta cartão (observar lineName e
            listar os aplicáveis da instituição).
             Example: LIMITE_CREDITO_TOTAL.
        consolidation_type (EnumCreditCardAccountsConsolidationType): Indicador que permite informar se o valor do
            limite é consolidado ou individual.

            CONSOLIDADO: utilizado quando o limite da conta cartão é compartilhado entre todos os métodos de pagamento
            (paymentMethod) atrelados a conta.

            INDIVIDUAL: Utilizado quando cada método de pagamento (paymentMethod) possui seu limite segregado.
             Example: CONSOLIDADO.
        identification_number (str): Número de identificação do cartão: corresponde aos 4 últimos dígitos do cartão para
            PF, ou então, preencher com um identificador para PJ, com as caracteristicas definidas para os IDs no Open
            Finance.
             Example: 4453.
        is_limit_flexible (bool): True= Indica que a conta cartão possui limite total flexível ou “sem limite”. False =
            Indica que a conta cartão possui limite predeterminado exibido no canal para o cliente. Example: True.
        used_amount (CreditCardsUsedAmount): Valor utilizado do limite informado
        line_name (CreditCardAccountsLimitsDataLineName | Unset):  Example: CREDITO_A_VISTA.
        line_name_additional_info (str | Unset): Campo de preenchimento obrigatório se selecionada a opção 'OUTRAS' em
            lineName. Example: Informações adicionais e complementares..
        limit_amount (CreditCardsLimitAmount | Unset): Valor total do limite concedido.
        available_amount (CreditCardsAvailableAmount | Unset): Valor disponível do limite informado
        customized_limit_amount (CreditCardAccountsLimitsDataCustomizedLimitAmount | Unset): Valor total do limite
            customizado pelo cliente nos canais eletrônicos da instituição. Esse objeto é de envio obrigatório nos casos em
            que a instituição permita ao cliente alterar o seu limite.
    """

    credit_line_limit_type: EnumCreditCardAccountsLineLimitType
    consolidation_type: EnumCreditCardAccountsConsolidationType
    identification_number: str
    is_limit_flexible: bool
    used_amount: 'CreditCardsUsedAmount'
    line_name: CreditCardAccountsLimitsDataLineName | Unset = UNSET
    line_name_additional_info: str | Unset = UNSET
    limit_amount: 'CreditCardsLimitAmount | Unset' = UNSET
    available_amount: 'CreditCardsAvailableAmount | Unset' = UNSET
    customized_limit_amount: (
        'CreditCardAccountsLimitsDataCustomizedLimitAmount | Unset'
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        credit_line_limit_type = self.credit_line_limit_type.value

        consolidation_type = self.consolidation_type.value

        identification_number = self.identification_number

        is_limit_flexible = self.is_limit_flexible

        used_amount = self.used_amount.to_dict()

        line_name: str | Unset = UNSET
        if not isinstance(self.line_name, Unset):
            line_name = self.line_name.value

        line_name_additional_info = self.line_name_additional_info

        limit_amount: dict[str, Any] | Unset = UNSET
        if not isinstance(self.limit_amount, Unset):
            limit_amount = self.limit_amount.to_dict()

        available_amount: dict[str, Any] | Unset = UNSET
        if not isinstance(self.available_amount, Unset):
            available_amount = self.available_amount.to_dict()

        customized_limit_amount: dict[str, Any] | Unset = UNSET
        if not isinstance(self.customized_limit_amount, Unset):
            customized_limit_amount = self.customized_limit_amount.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "creditLineLimitType": credit_line_limit_type,
                "consolidationType": consolidation_type,
                "identificationNumber": identification_number,
                "isLimitFlexible": is_limit_flexible,
                "usedAmount": used_amount,
            }
        )
        if line_name is not UNSET:
            field_dict["lineName"] = line_name
        if line_name_additional_info is not UNSET:
            field_dict["lineNameAdditionalInfo"] = line_name_additional_info
        if limit_amount is not UNSET:
            field_dict["limitAmount"] = limit_amount
        if available_amount is not UNSET:
            field_dict["availableAmount"] = available_amount
        if customized_limit_amount is not UNSET:
            field_dict["customizedLimitAmount"] = customized_limit_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from clients.credit_cards_v2_3_1.models.credit_card_accounts_limits_data_customized_limit_amount import (
            CreditCardAccountsLimitsDataCustomizedLimitAmount,
        )
        from clients.credit_cards_v2_3_1.models.credit_cards_available_amount import CreditCardsAvailableAmount
        from clients.credit_cards_v2_3_1.models.credit_cards_limit_amount import CreditCardsLimitAmount
        from clients.credit_cards_v2_3_1.models.credit_cards_used_amount import CreditCardsUsedAmount

        d = dict(src_dict)
        credit_line_limit_type = EnumCreditCardAccountsLineLimitType(
            d.pop("creditLineLimitType")
        )

        consolidation_type = EnumCreditCardAccountsConsolidationType(
            d.pop("consolidationType")
        )

        identification_number = d.pop("identificationNumber")

        is_limit_flexible = d.pop("isLimitFlexible")

        used_amount = CreditCardsUsedAmount.from_dict(d.pop("usedAmount"))

        _line_name = d.pop("lineName", UNSET)
        line_name: CreditCardAccountsLimitsDataLineName | Unset
        if isinstance(_line_name, Unset):
            line_name = UNSET
        else:
            line_name = CreditCardAccountsLimitsDataLineName(_line_name)

        line_name_additional_info = d.pop("lineNameAdditionalInfo", UNSET)

        _limit_amount = d.pop("limitAmount", UNSET)
        limit_amount: 'CreditCardsLimitAmount | Unset'
        if isinstance(_limit_amount, Unset):
            limit_amount = UNSET
        else:
            limit_amount = CreditCardsLimitAmount.from_dict(_limit_amount)

        _available_amount = d.pop("availableAmount", UNSET)
        available_amount: 'CreditCardsAvailableAmount | Unset'
        if isinstance(_available_amount, Unset):
            available_amount = UNSET
        else:
            available_amount = CreditCardsAvailableAmount.from_dict(_available_amount)

        _customized_limit_amount = d.pop("customizedLimitAmount", UNSET)
        customized_limit_amount: (
            'CreditCardAccountsLimitsDataCustomizedLimitAmount | Unset'
        )
        if isinstance(_customized_limit_amount, Unset):
            customized_limit_amount = UNSET
        else:
            customized_limit_amount = (
                CreditCardAccountsLimitsDataCustomizedLimitAmount.from_dict(
                    _customized_limit_amount
                )
            )

        credit_card_accounts_limits_data = cls(
            credit_line_limit_type=credit_line_limit_type,
            consolidation_type=consolidation_type,
            identification_number=identification_number,
            is_limit_flexible=is_limit_flexible,
            used_amount=used_amount,
            line_name=line_name,
            line_name_additional_info=line_name_additional_info,
            limit_amount=limit_amount,
            available_amount=available_amount,
            customized_limit_amount=customized_limit_amount,
        )

        credit_card_accounts_limits_data.additional_properties = d
        return credit_card_accounts_limits_data

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
