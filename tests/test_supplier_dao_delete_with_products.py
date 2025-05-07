import pytest
from unittest.mock import patch
from inventory.suplier_dao import SupplierDAO

@pytest.fixture
def mock_db_cursor():
    with patch("inventory.database.Database.get_cursor") as mock_cursor:
        yield mock_cursor

def test_supplier_dao_delete_with_products(mock_db_cursor):
    mock_cursor_instance = mock_db_cursor.return_value.__enter__.return_value
    mock_cursor_instance.fetchone.return_value = (0,)
    result = SupplierDAO.delete_supplier(1)
    assert result is True
