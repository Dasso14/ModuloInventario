import pytest
from datetime import datetime
from inventory.models.product import Product
from inventory.dao.product_dao import ProductDAO
from inventory.database import Database

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Database.initialize()
    yield
    Database.close_all()

def test_create_product():
    now = datetime.utcnow()
    product = Product(
        product_id=0,
        sku="TEST123",
        name="Producto Test",
        description="Producto de prueba",
        category_id=1,
        supplier_id=1,
        unit_cost=10.0,
        unit_price=15.0,
        unit_measure="unidad",
        weight=1.0,
        volume=0.5,
        min_stock=5,
        max_stock=50,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    product_id = ProductDAO.create(product)
    assert isinstance(product_id, int)
