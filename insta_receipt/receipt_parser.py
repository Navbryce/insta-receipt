import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import TextIO

from bs4 import BeautifulSoup
import re

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
        return re.sub('\s+', ' ', value)

    @staticmethod
    def parse_price(value: str) -> float:
        return float(re.sub('^\$', '', value))

    def parse(self, file: TextIO):
        soup = BeautifulSoup(file, 'html.parser')
        store, order_placed = self.__get_store_and_time(soup)
        items = [self.__get_receipt_item(item_element) for item_element in soup.find_all(class_='item-row item-delivered')]
        charges = self.__get_charges(soup.find(class_='charges'))
        receipt = Receipt(
            store=store,
            order_placed=order_placed,
            items=items,
            tax=charges.tax,
            tip=charges.tip,
            service_fee=charges.fee,
            refunds=[] # TODO: Parse refunds
        )
        if receipt.total != receipt.total:
            raise ValueError(f'Calculated total {receipt.total} does not equal actual total {charges.total}')
        return receipt

    __STORE_REGEX = 'from (.*) was'
    __DATETIME_REGEX = 'on (.*) and'
    def __get_store_and_time(self, soup: BeautifulSoup) -> [str, datetime]:
        haystack = soup.find(class_="DriverDeliverySchedule").get_text()
        store = re.search(self.__STORE_REGEX, haystack).groups()[0]
        datetime_str = re.search(self.__DATETIME_REGEX, haystack).groups()[0]
        return store, datetime.strptime(re.sub(r'(\d)(st|nd|rd|th)', r'\1', datetime_str), "%B %d, %Y")



    def __get_receipt_item(self, item_element) -> ReceiptItem:
        name = item_element.find(class_="item-name")
        name.find(class_="muted").extract()
        name = ReceiptParser.remove_all_new_lines(name.get_text())
        return ReceiptItem(
            name=name,
            cost= ReceiptParser.parse_price(item_element.find(class_='total').get_text())
        )

    CHARGES_KEYS_ORDERING = ['subtotal', 'tax', 'tip', 'fee', 'total']
    def __get_charges(self, charges_element) -> Charges:
        charges = {}
        charges_rows = charges_element.find_all('tr')
        for row, charge_key in zip(charges_rows, self.CHARGES_KEYS_ORDERING):
            charge_type = row.find(class_='charge-type').get_text().lower()
            if charge_key not in charge_type:
                raise ValueError(f'Possible charges ordering change. Expected charge type containing {charge_key}. Found {charge_type}')
            charges[charge_key] = ReceiptParser.parse_price(row.find(class_='amount').get_text())
        return Charges(**charges)

