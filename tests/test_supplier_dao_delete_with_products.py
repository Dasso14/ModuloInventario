import pytest
from unittest.mock import MagicMock, patch
from inventory.dao.supplier_dao import SupplierDAO # type: ignore
from inventory.exceptions import SupplierHasProductsError # type: ignore

def test_supplier_dao_delete_with_products(mock_db_cursor):
    # Configurar mocks para verificar restricciones de integridad
    mock_db_cursor.execute.side_effect = [
        None,  # Primera llamada (verificación de productos)
        MagicMock(rowcount=1)  # Segunda llamada (DELETE real)
    ]
    
    # Mockear la verificación de productos asociados
    with patch("inventory.dao.supplier_dao.ProductDAO.get_by_supplier") as mock_get:
        # Caso 1: Proveedor sin productos
        mock_get.return_value = []
        SupplierDAO.delete(1)
        mock_db_cursor.execute.assert_called_with(
            "DELETE FROM suppliers WHERE supplier_id = %s", (1,)
        )

        # Caso 2: Proveedor con productos
        mock_get.return_value = [MagicMock()]  # Simular productos existentes
        with pytest.raises(SupplierHasProductsError):
            SupplierDAO.delete(2)