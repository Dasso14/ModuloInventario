from dataclasses import dataclass
from datetime import datetime

@dataclass
class Product:
    product_id: int
    sku: str
    name: str
    description: str
    category_id: int
    supplier_id: int
    unit_cost: float
    unit_price: float
    unit_measure: str
    weight: float
    volume: float
    min_stock: int
    max_stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime