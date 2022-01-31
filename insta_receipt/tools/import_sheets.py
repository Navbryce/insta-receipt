import json
import sys

from insta_receipt import TEMPLATE_PATH
from insta_receipt.google_sheets import service, Sheet, GridData, RowData

__SPREAD_SHEET_ID = "1LasEqoEVF2uq4dBC9oAbNjdHfL2h0bqSt2TdvTzVxUQ"
__TEMPLATE_SHEET_NAMES = ["Payments", "_ItemsMeta", "_RefundsMeta"]

__FIELDS_FOR_TEMPLATE = "sheets(data(startRow,startColumn,rowData),protectedRanges(protectedRangeId,range,warningOnly,requestingUserCanEdit),conditionalFormats,properties(sheetId,title,index,hidden,tabColor))"


def main():
    if len(sys.argv) < 1:
        raise TypeError("Not enough arguments")
    request = (
        service.get_sheets_service()
        .spreadsheets()
        .get(spreadsheetId=__SPREAD_SHEET_ID, fields=__FIELDS_FOR_TEMPLATE)
    )
    sheets = [__clean_sheet(sheet) for sheet in request.execute()["sheets"]]
    with open(TEMPLATE_PATH, "w") as f:
        json.dump(sheets, f)
    print(f"Wrote templates to {TEMPLATE_PATH}")


def __clean_sheet(sheet: Sheet) -> Sheet:
    return {
        **sheet,
        "data": __clean_up_data(sheet["data"]),
    }


def __clean_up_data(data: [GridData]) -> [GridData]:
    last_grid_data = data[-1]
    last_data_row_index = 0
    if "rowData" not in last_grid_data:
        return data
    for index, row in reversed(list(enumerate(last_grid_data["rowData"]))):
        if not __is_empty_row(row):
            last_data_row_index = index
            break
    last_grid_data["rowData"] = last_grid_data["rowData"][0 : last_data_row_index + 1]
    return data[0:-1] + [last_grid_data]


def __is_empty_row(row: RowData) -> bool:
    for value in row["values"]:
        if "userEnteredValue" in value:
            return False
    return True


if __name__ == "__main__":
    main()
