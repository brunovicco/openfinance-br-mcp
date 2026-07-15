"""Treasure Titles API model: Objeto para detalhamento de remuneração do titulo."""

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from clients.treasure_titles_v1_1_0.models.treasure_titles_calculation import TreasureTitlesCalculation
from clients.treasure_titles_v1_1_0.models.treasure_titles_indexer import TreasureTitlesIndexer
from clients.treasure_titles_v1_1_0.models.treasure_titles_rate_periodicity import TreasureTitlesRatePeriodicity
from clients.treasure_titles_v1_1_0.types import UNSET, Unset

T = TypeVar("T", bound="TreasureTitlesRemuneration")


@_attrs_define
class TreasureTitlesRemuneration:
    """Objeto para detalhamento de remuneração do titulo.

    Attributes:
        indexer (TreasureTitlesIndexer): Índice utilizado como referência para a correção da rentabilidade e/ou
            rendimentos do ativo (CDI, DI , TR, IPCA, IGP_M, IGP_DI, INPC, BCP, TLC, SELIC, PRE_FIXADO e OUTROS) Example:
            CDI.
        rate_periodicity (TreasureTitlesRatePeriodicity): Periodicidade da taxa de remuneração (mensal, anual, diário e
            semestral) Example: DIARIO.
        calculation (TreasureTitlesCalculation): Base de cálculo (dias úteis ou dias corridos) Example: DIAS_CORRIDOS.
        indexer_additional_info (str | Unset): Informações adicionais do indexador.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo 'indexer' for preenchido com o
            valor 'OUTROS'.
             Example: Dólar.
        pre_fixed_rate (str | Unset): Valor da taxa da aquisição do contrato.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando houver `PRE_FIXADO` no campo `indexer`
            ou quando se tratar de produto com remuneração híbrida.
             Example: 0.300000.
        post_fixed_indexer_percentage (str | Unset): Percentual do indexador da aquisição do contrato.

            [Restrição] Campo de preenchimento obrigatório pelas participantes quando o campo `indexer` for preenchido de
            forma diferente de `PRE_FIXADO` ou quando se tratar de produto com remuneração híbrida.
             Example: 1.100000.
    """

    indexer: TreasureTitlesIndexer
    rate_periodicity: TreasureTitlesRatePeriodicity
    calculation: TreasureTitlesCalculation
    indexer_additional_info: str | Unset = UNSET
    pre_fixed_rate: str | Unset = UNSET
    post_fixed_indexer_percentage: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        indexer = self.indexer.value

        rate_periodicity = self.rate_periodicity.value

        calculation = self.calculation.value

        indexer_additional_info = self.indexer_additional_info

        pre_fixed_rate = self.pre_fixed_rate

        post_fixed_indexer_percentage = self.post_fixed_indexer_percentage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "indexer": indexer,
                "ratePeriodicity": rate_periodicity,
                "calculation": calculation,
            }
        )
        if indexer_additional_info is not UNSET:
            field_dict["indexerAdditionalInfo"] = indexer_additional_info
        if pre_fixed_rate is not UNSET:
            field_dict["preFixedRate"] = pre_fixed_rate
        if post_fixed_indexer_percentage is not UNSET:
            field_dict["postFixedIndexerPercentage"] = post_fixed_indexer_percentage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        indexer = TreasureTitlesIndexer(d.pop("indexer"))

        rate_periodicity = TreasureTitlesRatePeriodicity(d.pop("ratePeriodicity"))

        calculation = TreasureTitlesCalculation(d.pop("calculation"))

        indexer_additional_info = d.pop("indexerAdditionalInfo", UNSET)

        pre_fixed_rate = d.pop("preFixedRate", UNSET)

        post_fixed_indexer_percentage = d.pop("postFixedIndexerPercentage", UNSET)

        treasure_titles_remuneration = cls(
            indexer=indexer,
            rate_periodicity=rate_periodicity,
            calculation=calculation,
            indexer_additional_info=indexer_additional_info,
            pre_fixed_rate=pre_fixed_rate,
            post_fixed_indexer_percentage=post_fixed_indexer_percentage,
        )

        treasure_titles_remuneration.additional_properties = d
        return treasure_titles_remuneration

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
