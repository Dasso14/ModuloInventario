import pytest
from inventory.models.product import Product
from inventory.dao.product_dao import ProductDAO
from datetime import datetime

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    from inventory.database import Database
    Database.initialize()
    yield
    Database.close_all()

def test_inventory_transaction():
    now = datetime.utcnow()
    product = Product(
        product_id=0,
        sku="TRANS123",
        name="Producto Transacción",
        description="Producto para prueba de transacción",
        category_id=1,
        supplier_id=1,
        unit_cost=20.0,
        unit_price=30.0,
        unit_measure="unidad",
        weight=2.0,
        volume=1.0,
        min_stock=10,
        max_stock=100,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    product_id = ProductDAO.create(product)
    assert isinstance(product_id, int)