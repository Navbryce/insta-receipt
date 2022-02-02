from __future__ import print_function

import sys
from google_sheets import service
from insta_receipt.google_spreadsheet_generator import GoogleSpreadSheetGenerator
from insta_receipt.receipt_parser import ReceiptParser


def main():
    if len(sys.argv) < 2:
        print("Provide receipt path")
    with open(sys.argv[1], "r") as f:
        receipt = ReceiptParser().parse(f)

    res = (
        service.get_sheets_service()
        .spreadsheets()
        .create(body=GoogleSpreadSheetGenerator().generate_spreadsheet(receipt))
        .execute()
    )
    print(res["spreadsheetUrl"])


if __name__ == "__main__":
    main()
