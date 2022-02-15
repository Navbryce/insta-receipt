from dataclasses import dataclass


@dataclass
class ReceiptItem:
    name: str
    cost: float
    unit_price: float
    quantity: int
