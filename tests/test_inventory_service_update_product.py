from unittest.mock import MagicMock, patch
import pytest
from inventory.services.inventory_service import InventoryService


def test_inventory_service_update_product():
    service = InventoryService()
    
    update_data = {
        "sku": "NEW-001",
        "name": "Producto Actualizado",
        "unit_measure": "caja",  
        "unit_price": 25.99
    }

    with patch("inventory.dao.product_dao.ProductDAO.get_by_sku") as mock_sku:
        mock_sku.return_value = None  
        
        with patch("inventory.dao.product_dao.ProductDAO.update") as mock_update:
            mock_update.return_value = True
            
            result = service.update_product(1, update_data)
            assert result is True
            
            args, _ = mock_update.call_args
            updated_product = args[0]
            assert updated_product.unit_measure == "caja"  

    with patch("inventory.dao.product_dao.ProductDAO.get_by_sku") as mock_sku:
        mock_sku.return_value = MagicMock()  # SKU ya existe
        with pytest.raises(ValueError, match="SKU ya está en uso"):
            service.update_product(1, {"sku": "DUPLICADO-001"})