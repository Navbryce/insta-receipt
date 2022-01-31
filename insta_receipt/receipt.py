from dataclasses import dataclass
from datetime import datetime

from insta_receipt.receipt_item import ReceiptItem


@dataclass
class Receipt:
    store: str
    order_placed: datetime
    items: [ReceiptItem]
    tax: float
    tip: float
    service_fee: float
    refunds: [ReceiptItem]

    @property
    def subtotal(self) -> float:
        return sum([item.cost for item in self.items])

    @property
    def total_refunds(self) -> float:
        return sum([item.cost for item in self.refunds])

    @property
    def total(self) -> float:
        return (
            self.subtotal + self.tax + self.tip + self.service_fee + self.total_refunds
        )
