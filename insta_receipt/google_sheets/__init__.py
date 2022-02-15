from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Optional, Union, Dict


@dataclass
class ExtendedValue:
    formulaValue: Optional[str] = None
    numberValue: Optional[float] = None
    stringValue: Optional[str] = None

@dataclass
class NumberFormat:
    pattern: str
    type: str = "NUMBER"

@dataclass
class CellFormat:
    numberFormat: Optional[NumberFormat] = None

@dataclass
class CellData:
    @staticmethod
    def from_value(value: Union[str, float, ExtendedValue]) -> CellData:
        if isinstance(value, str):
            return CellData(ExtendedValue(stringValue=value))
        if isinstance(value, (float, int)):
            return CellData(ExtendedValue(numberValue=value))
        if isinstance(value, ExtendedValue):
            return CellData(value)
        raise ValueError(f"Unsupported type {type(value)}")

    userEnteredValue: ExtendedValue
    userEnteredFormat: Optional[CellFormat] = None


CellTypes = Union[CellData, str, float]


@dataclass
class RowData:
    @staticmethod
    def from_list(data: [CellTypes]) -> RowData:
        return RowData(
            values=[
                value if isinstance(value, CellData) else CellData.from_value(value)
                for value in data
            ]
        )

    values: [CellData]


@dataclass
class GridData:
    @staticmethod
    def from_list(data: [[CellTypes]]) -> GridData:
        return GridData(rowData=[RowData.from_list(row) for row in data])

    startRow = 0
    startColumn = 0
    rowData: [RowData]


@dataclass
class SheetProperties:
    title: str


@dataclass
class Sheet:
    data: [GridData]
    properties: SheetProperties


@dataclass
class SpreadsheetProperties:
    title: str


@dataclass
class Spreadsheet:
    sheets: [Sheet]
    properties: SpreadsheetProperties

    def to_serializable(self) -> Dict:
        return dataclasses.asdict(self)
