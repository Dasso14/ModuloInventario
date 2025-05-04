from dataclasses import dataclass
from datetime import datetime


@dataclass
class Product:
    sku: str
    name: str
    category_id: int
    supplier_id: int
    unit_cost: float
    unit_price: float
    unit_measure: str

    # Campos opcionales
    product_id: int = None
    description: str = None
    weight: float = 0.0
    volume: float = 0.0
    min_stock: int = 0
    max_stock: int = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def __post_init__(self):
        if self.unit_price <= self.unit_cost:
            raise ValueError("El precio debe ser mayor al costo")
        if self.min_stock < 0:
            raise ValueError("Stock mínimo no puede ser negativo")