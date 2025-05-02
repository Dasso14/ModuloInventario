import pytest
from unittest.mock import MagicMock, patch

from inventory.suplier_dao import SupplierDAO

def test_supplier_dao_delete_with_products(mock_db_cursor):
    mock_db_cursor.execute.side_effect = [
        None,  
        MagicMock(rowcount=1)  
    ]
    
    with patch("inventory.dao.supplier_dao.ProductDAO.get_by_supplier") as mock_get:
        
        mock_get.return_value = []
        SupplierDAO.delete(1)
        mock_db_cursor.execute.assert_called_with(
            "DELETE FROM suppliers WHERE supplier_id = %s", (1,)
        )

        mock_get.return_value = [MagicMock()]  
        with pytest.raises(SupplierHasProductsError): # type: ignore
            SupplierDAO.delete(2)