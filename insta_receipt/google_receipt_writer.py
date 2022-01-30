import dataclasses
import json

from insta_receipt import TEMPLATE_PATH
from insta_receipt.google_sheets import Spreadsheet, GridData, Sheet, SpreadsheetProperties
from insta_receipt.receipt import Receipt
from insta_receipt.receipt_item import ReceiptItem


class GoogleReceiptWriter:

    def __init__(self, spreadsheets_service):
        self.spreadssheets_service = spreadsheets_service
        pass

    def write_receipt(self, receipt: Receipt) -> str:
        template_sheets = self.__load_template_sheets(TEMPLATE_PATH)
        return self.__write_spreadsheet(Spreadsheet(
            sheets=[
                self.__build_items_sheet(template_sheets[0], receipt.items),
                self.__build_refunds_sheet(template_sheets[1], receipt.refunds),
                self.__build_charges_sheet(template_sheets[2], receipt)
            ] + template_sheets[3:],
            properties=SpreadsheetProperties(title=f'InstaReceipt: {receipt.store} {receipt.order_placed.date().isoformat()}')
        ))

    def __build_items_sheet(self, template: Sheet, items: [ReceiptItem]) -> Sheet:
        rows = [['Item', 'Cost', 'Person']] + [[item.name, item.cost] for item in items]
        return Sheet(properties=template["properties"], data=GridData.from_list(rows))

    def __build_refunds_sheet(self, template: Sheet, refunds: [float]) -> Sheet:
        rows = [['Refunds', 'Person']] + [['', value] for value in refunds]
        return Sheet(properties=template["properties"], data=GridData.from_list(rows))

    def __build_charges_sheet(self, template: Sheet, receipt: Receipt) -> Sheet:
        rows = [['Subtotal', receipt.subtotal],
                ['Tax', receipt.tax],
                ['Tip', receipt.tip],
                ['Service Fee', receipt.service_fee],
                ['Total Refunds', receipt.total_refunds],
                ['Total', receipt.total]]
        return Sheet(properties=template["properties"], data=GridData.from_list(rows))

    def __load_template_sheets(self, template_path) -> [Sheet]:
        # TODO: Technically return type is wrong here. Maybe fix in the future
        with open(template_path, 'r') as f:
            return json.load(f)


    def __write_spreadsheet(self, spreadsheet: Spreadsheet) -> str:
        res = self.spreadssheets_service.create(
            body=dataclasses.asdict(spreadsheet),
        ).execute()
        return res["spreadsheetUrl"]

