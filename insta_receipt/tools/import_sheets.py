import json
import sys

from insta_receipt import TEMPLATE_PATH
from insta_receipt.google_sheets import service

__SPREAD_SHEET_ID= '1LasEqoEVF2uq4dBC9oAbNjdHfL2h0bqSt2TdvTzVxUQ'
__TEMPLATE_SHEET_NAMES=["Payments", "_ItemsMeta", "_RefundsMeta"]

__FIELDS_FOR_TEMPLATE= "sheets(data,properties(title,index,hidden,tabColor))"

def main():
    if len(sys.argv) < 1:
        raise TypeError("Not enough arguments")
    request = service.get_sheets_service().spreadsheets().get(spreadsheetId=__SPREAD_SHEET_ID, fields=__FIELDS_FOR_TEMPLATE)
    with open(TEMPLATE_PATH, 'w') as f:
        json.dump(request.execute()["sheets"], f)
    print(f"Wrote templates to {TEMPLATE_PATH}")
if __name__ == '__main__':
    main()