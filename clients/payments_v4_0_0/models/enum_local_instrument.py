"""EnumLocalInstrument: enum of possible values (DICT, INIC, MANU, QRDN, QRES) for this field, per the Payments OpenAPI spec."""

from enum import Enum


class EnumLocalInstrument(str, Enum):
    DICT = "DICT"
    INIC = "INIC"
    MANU = "MANU"
    QRDN = "QRDN"
    QRES = "QRES"

    def __str__(self) -> str:
        return str(self.value)
