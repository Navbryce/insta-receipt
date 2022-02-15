import re
from dataclasses import dataclass
from datetime import datetime
from typing import TextIO

from bs4 import BeautifulSoup

from insta_receipt.receipt import Receipt
from insta_receipt.receipt_item import ReceiptItem


@dataclass
class Charges:
    subtotal: float
    tax: float
    tip: float
    fee: float
    total: float


class ReceiptParser:
    @staticmethod
    def remove_all_new_lines(value: str) -> str:
        return re.sub(r"\s+", " ", value)

    @staticmethod
    def parse_price(value: str) -> float:
        return float(re.sub(r"\$", "", value))

    def parse(self, file: TextIO):
        soup = BeautifulSoup(file, "html5lib")
        store, order_placed = self.__get_store_and_time(soup)
        items = [
            self.__get_receipt_item(item_element)
            for item_element in soup.find_all(class_=["item-delivered"])
        ]
        refunds = list(
            filter(
                lambda x: x.cost < 0,
                [
                    self.__get_receipt_item(item_element)
                    for item_element in soup.find_all(class_="item-row item-refunded")
                ],
            )
        )
        charges = self.__get_charges(soup.find(class_="charges"))
        receipt = Receipt(
            store=store,
            order_placed=order_placed,
            items=items,
            tax=charges.tax,
            tip=charges.tip,
            subtotal=charges.subtotal,
            service_fee=charges.fee,
            refunds=refunds,
        )
        if receipt.total != receipt.total:
            raise ValueError(
                f"Calculated total {receipt.total} does not equal actual total {charges.total}"
            )
        return receipt

    __STORE_REGEX = "from (.*) was"
    __DATETIME_REGEX = "on (.*) and"

    def __get_store_and_time(self, soup: BeautifulSoup) -> [str, datetime]:
        haystack = soup.find(class_="DriverDeliverySchedule").get_text()
        store = re.search(self.__STORE_REGEX, haystack).groups()[0]
        datetime_str = re.search(self.__DATETIME_REGEX, haystack).groups()[0]
        return store, datetime.strptime(
            re.sub(r"(\d)(st|nd|rd|th)", r"\1", datetime_str), "%B %d, %Y"
        )

    def __get_receipt_item(self, item_element) -> ReceiptItem:
        name = item_element.find(class_="item-name")
        cost = ReceiptParser.parse_price(
            item_element.find_all(class_="total")[-1].get_text()
        )
        if cost == 0.:
            return ReceiptItem(name=name, cost=cost, unit_price=0, quantity=0)
        unit_price, quantity = self.__get_unit_price_and_quantity(name.find(class_="muted").extract())
        name = ReceiptParser.remove_all_new_lines(name.get_text())
        return ReceiptItem(
            name=name,
            cost=cost,
            unit_price=cost / quantity, # the receipt cost has been rounded, so the unit price needs to be updated
            quantity=quantity
        )
    def __get_unit_price_and_quantity(self, element) -> [float, float]:
        quantity_haystack, unit_price_str = element.get_text().split("x")
        last_quantity_line = quantity_haystack.split("\n")[-1]
        quantity = float(last_quantity_line.strip().split(" ")[0])
        return ReceiptParser.parse_price(unit_price_str), quantity



    CHARGE_KEYS = ["subtotal", "tax", "tip", "fee", "total"]

    def __get_charges(self, charges_element) -> Charges:
        charges = {}
        charges_rows = charges_element.find_all("tr")
        for row in charges_rows:
            charge_type = row.find(class_="charge-type").get_text().lower()
            charge_key = next(
                (key for key in self.CHARGE_KEYS if key in charge_type), None
            )
            if charge_key is None:
                continue
            charges[charge_key] = ReceiptParser.parse_price(
                row.find(class_="amount").get_text()
            )
        return Charges(**charges)
