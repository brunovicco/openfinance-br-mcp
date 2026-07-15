"""Bank Fixed Incomes API model: Objeto para detalhamento de remuneração do titulo."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from clients.bank_fixed_incomes_v1_1_0.models.enum_bank_fixed_income_indexer import EnumBankFixedIncomeIndexer
from clients.bank_fixed_incomes_v1_1_0.models.enum_calculation import EnumCalculation
from clients.bank_fixed_incomes_v1_1_0.models.enum_rate_periodicity import EnumRatePeriodicity
from clients.bank_fixed_incomes_v1_1_0.models.enum_rate_type import EnumRateType
from clients.bank_fixed_incomes_v1_1_0.types import UNSET, Unset

T = TypeVar("T", bound="Remuneration")


@_attrs_define
class Remuneration:
    """Objeto para detalhamento de remuneração do titulo.

    Attributes:
        rate_type (EnumRateType): "Tipo da taxa de remuneração (linear ou exponencial)"
             Example: LINEAR.
        rate_periodicity (EnumRatePeriodicity): Periodicidade da taxa de remuneração (mensal, anual, diário, semestral)
             Example: MENSAL.
        calculation (EnumCalculation): "Base de cálculo (dias úteis ou dias corridos)"
             Example: DIAS_CORRIDOS.
        indexer (EnumBankFixedIncomeIndexer): Índice utilizado como referência para a correção da rentabilidade e/ou
            rendimentos do ativo (CDI, DI , TR, IPCA, IGP_M, IGP_DI, INPC, BCP, TLC, SELIC, PRE_FIXADO e OUTROS) Example:
            CDI.
        pre_fixed_rate (str | Unset): Taxa de remuneração pré fixada de emissão do título.  p.ex. 0.014500.

            O preenchimento deve respeitar as 6 casas decimais, mesmo que venham preenchidas com zeros(representação de
            porcentagem p.ex: 0.150000. Este valor representa 15%. O valor 1 representa 100%).

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando houver 'PRE_FIXADO' no campo 'indexer'
            ou quando se tratar de produto com remuneração híbrida.
             Example: 0.300000.
        post_fixed_indexer_percentage (str | Unset): Percentual do indexador pós fixado de emissão do  título.  p.ex.
            0.014500.

            O preenchimento deve respeitar as 6 casas decimais, mesmo que venham preenchidas com zeros(representação de
            porcentagem p.ex: 0.150000. Este valor representa 15%. O valor 1 representa 100%).

            Um valor negativo neste campo indica que a taxa do indexador está sendo deduzida (descontada) da rentabilidade
            final do produto, em vez de ser acrescida.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'indexer' for preenchido de
            forma diferente de 'PRE_FIXADO' ou quando se tratar de produto com remuneração híbrida.
             Example: 1.100000.
        indexer_additional_info (str | Unset): Informações adicionais do indexador

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando houver 'Outros' no campo 'indexer'.
             Example: Dólar.
    """

    rate_type: EnumRateType
    rate_periodicity: EnumRatePeriodicity
    calculation: EnumCalculation
    indexer: EnumBankFixedIncomeIndexer
    pre_fixed_rate: str | Unset = UNSET
    post_fixed_indexer_percentage: str | Unset = UNSET
    indexer_additional_info: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        rate_type = self.rate_type.value

        rate_periodicity = self.rate_periodicity.value

        calculation = self.calculation.value

        indexer = self.indexer.value

        pre_fixed_rate = self.pre_fixed_rate

        post_fixed_indexer_percentage = self.post_fixed_indexer_percentage

        indexer_additional_info = self.indexer_additional_info

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "rateType": rate_type,
                "ratePeriodicity": rate_periodicity,
                "calculation": calculation,
                "indexer": indexer,
            }
        )
        if pre_fixed_rate is not UNSET:
            field_dict["preFixedRate"] = pre_fixed_rate
        if post_fixed_indexer_percentage is not UNSET:
            field_dict["postFixedIndexerPercentage"] = post_fixed_indexer_percentage
        if indexer_additional_info is not UNSET:
            field_dict["indexerAdditionalInfo"] = indexer_additional_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rate_type = EnumRateType(d.pop("rateType"))

        rate_periodicity = EnumRatePeriodicity(d.pop("ratePeriodicity"))

        calculation = EnumCalculation(d.pop("calculation"))

        indexer = EnumBankFixedIncomeIndexer(d.pop("indexer"))

        pre_fixed_rate = d.pop("preFixedRate", UNSET)

        post_fixed_indexer_percentage = d.pop("postFixedIndexerPercentage", UNSET)

        indexer_additional_info = d.pop("indexerAdditionalInfo", UNSET)

        remuneration = cls(
            rate_type=rate_type,
            rate_periodicity=rate_periodicity,
            calculation=calculation,
            indexer=indexer,
            pre_fixed_rate=pre_fixed_rate,
            post_fixed_indexer_percentage=post_fixed_indexer_percentage,
            indexer_additional_info=indexer_additional_info,
        )

        return remuneration
