from inventory.models.product import Product
from datetime import datetime

def test_product_model():
    now = datetime.utcnow()
    product = Product(
        product_id=1,
        sku="MODEL123",
        name="Producto Modelo",
        description="Producto para prueba de modelo",
        category_id=1,
        supplier_id=1,
        unit_cost=12.0,
        unit_price=18.0,
        unit_measure="unidad",
        weight=1.2,
        volume=0.6,
        min_stock=3,
        max_stock=30,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    assert product.sku == "MODEL123"
    assert product.name == "Producto Modelo"
