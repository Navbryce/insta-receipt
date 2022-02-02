import importlib
import json
import pkgutil

from insta_receipt.google_sheets import (
    Spreadsheet,
    GridData,
    Sheet,
    SpreadsheetProperties,
)
from insta_receipt.receipt import Receipt
from insta_receipt.receipt_item import ReceiptItem
from insta_receipt.tools.import_sheets import TEMPLATE_PATH


class GoogleSpreadSheetGenerator:
    def __init__(self):
        pass

    def generate_spreadsheet(self, receipt: Receipt) -> Spreadsheet:
        # TODO: Fix protected ranges for templates
        template_sheets = self.__load_template_sheets(TEMPLATE_PATH)
        return Spreadsheet(
            sheets=[
                self.__build_items_sheet(template_sheets[0], receipt.items),
                self.__build_charges_sheet(template_sheets[1], receipt),
            ]
            + template_sheets[2:],
            properties=SpreadsheetProperties(
                title=f"InstaReceipt: {receipt.store} {receipt.order_placed.date().isoformat()}"
            ),
        )

    def __build_items_sheet(self, template: Sheet, items: [ReceiptItem]) -> Sheet:
        rows = [["Item", "Cost", "Person"]] + [[item.name, item.cost] for item in items]
        return Sheet(properties=template["properties"], data=GridData.from_list(rows))

    def __build_charges_sheet(self, template: Sheet, receipt: Receipt) -> Sheet:
        rows = [
            ["Subtotal", receipt.effective_subtotal],
            ["Tax", receipt.tax],
            ["Tip", receipt.tip],
            ["Service Fee", receipt.service_fee],
            ["Fee Refunds", -receipt.fee_refunds],
            ["Total", receipt.total],
        ]
        return Sheet(properties=template["properties"], data=GridData.from_list(rows))

    def __load_template_sheets(self, template_path) -> [Sheet]:
        # TODO: Technically return type is wrong here. Maybe fix in the future
        return json.loads(pkgutil.get_data(__name__, template_path))
