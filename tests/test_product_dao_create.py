import pytest
from unittest.mock import MagicMock, patch
from inventory.dao.product_dao import ProductDAO
from inventory.models.product import Product
from datetime import datetime

@pytest.fixture
def mock_db_cursor():
    with patch("inventory.database.Database.get_cursor") as mock_db:
        mock_cursor = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_cursor
        yield mock_cursor

def test_product_dao_create(mock_db_cursor):
    mock_db_cursor.fetchone.return_value = [42]
    
    test_product = Product(
        product_id=0,
        sku="MOCK-001",
        name="Producto Mock",
        description="Descripción mock",
        category_id=1,
        supplier_id=1,
        unit_cost=10.0,
        unit_price=20.0,
        unit_measure="unidad",
        weight=0.5,
        volume=0.01,
        min_stock=5,
        max_stock=50,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    created_id = ProductDAO.create(test_product)
    
    assert created_id == 42
    mock_db_cursor.execute.assert_called_once()
    args, kwargs = mock_db_cursor.execute.call_args
    assert "INSERT INTO products" in args[0]
    assert args[1][1] == "Producto Mock"

def test_product_dao_get_by_id_not_found(mock_db_cursor):
    mock_db_cursor.fetchone.return_value = None
    
    result = ProductDAO.get_by_id(999)
    
    assert result is None
    mock_db_cursor.execute.assert_called_once_with(
        "SELECT * FROM products WHERE product_id = %s", (999,)
    )