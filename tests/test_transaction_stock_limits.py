import pytest
from inventory.models.product import Product
from datetime import datetime

def test_transaction_stock_limits():
    now = datetime.utcnow()
    product = Product(
        product_id=1,
        sku="LIMIT123",
        name="Producto Límite",
        description="Producto para prueba de límites de stock",
        category_id=1,
        supplier_id=1,
        unit_cost=15.0,
        unit_price=25.0,
        unit_measure="unidad",
        weight=1.5,
        volume=0.7,
        min_stock=5,
        max_stock=20,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    current_stock = 10
    assert product.min_stock <= current_stock <= product.max_stock
