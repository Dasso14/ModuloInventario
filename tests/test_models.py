from inventory.models.product import Product
from datetime import datetime

def test_create_product_model():
    now = datetime.now()
    product = Product(
        product_id=1,
        sku="ABC-123",
        name="Mouse",
        description="Mouse óptico",
        category_id=2,
        supplier_id=3,
        unit_cost=5.0,
        unit_price=10.0,
        unit_measure="unidad",
        weight=0.2,
        volume=0.01,
        min_stock=10,
        max_stock=100,
        is_active=True,
        created_at=now,
        updated_at=now
    )

    assert product.name == "Mouse"
    assert product.unit_price == 10.0
