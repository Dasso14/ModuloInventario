import re
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

        # Validar rangos y lógica de negocio
        if self.unit_price <= self.unit_cost:
            raise ValueError("El precio debe superar al costo en al menos 10%")
        if not re.match(r"^[A-Z]{3}-\d{4}$", self.sku):
            raise ValueError("SKU debe seguir el formato ABC-1234")
        if self.max_stock and self.max_stock < self.min_stock:
            raise ValueError("Stock máximo no puede ser menor al mínimo")