from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    transaction_id: int
    product_id: int
    location_id: int
    quantity: float
    transaction_type: str  # "in" o "out"
    transaction_date: datetime
