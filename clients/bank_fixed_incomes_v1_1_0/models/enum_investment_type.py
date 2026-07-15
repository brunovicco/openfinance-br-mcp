"""EnumInvestmentType: enum of possible values (CDB, LCA, LCI, RDB) for this field, per the Bank Fixed Incomes OpenAPI spec."""

from enum import Enum


class EnumInvestmentType(str, Enum):
    CDB = "CDB"
    LCA = "LCA"
    LCI = "LCI"
    RDB = "RDB"

    def __str__(self) -> str:
        return str(self.value)
