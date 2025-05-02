from unittest.mock import MagicMock, patch
import pytest
from inventory.services.inventory_service import InventoryService


def test_inventory_service_update_product():
    service = InventoryService()
    
    # Datos de prueba alineados con el esquema
    update_data = {
        "sku": "NEW-001",
        "name": "Producto Actualizado",
        "unit_measure": "caja",  # Usando el enum unit_measure
        "unit_price": 25.99
    }

    # Mockear verificación de SKU único
    with patch("inventory.dao.product_dao.ProductDAO.get_by_sku") as mock_sku:
        mock_sku.return_value = None  # SKU disponible
        
        # Mockear actualización en BD
        with patch("inventory.dao.product_dao.ProductDAO.update") as mock_update:
            mock_update.return_value = True
            
            # Caso válido
            result = service.update_product(1, update_data)
            assert result is True
            
            # Verificar que se usó el enum correctamente
            args, _ = mock_update.call_args
            updated_product = args[0]
            assert updated_product.unit_measure == "caja"  # Valor del enum

    # Caso inválido: SKU duplicado
    with patch("inventory.dao.product_dao.ProductDAO.get_by_sku") as mock_sku:
        mock_sku.return_value = MagicMock()  # SKU ya existe
        with pytest.raises(ValueError, match="SKU ya está en uso"):
            service.update_product(1, {"sku": "DUPLICADO-001"})