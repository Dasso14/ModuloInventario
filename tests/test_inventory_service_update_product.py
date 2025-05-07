from unittest.mock import patch, MagicMock
from inventory.services.inventory_service import InventoryService
from inventory.models.product import Product
from datetime import datetime

def test_inventory_service_update_product():
    service = InventoryService()
    now = datetime.utcnow()
    mock_product = Product(
        product_id=1,
        sku="NEW-001",
        name="Producto Original",
        description="Descripción original",
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

    update_data = {
        "sku": "NEW-001",
        "name": "Producto Actualizado",
        "unit_measure": "caja",
        "unit_price": 25.99
    }

    with patch.object(service.product_dao, 'get_by_sku', return_value=mock_product):
        with patch.object(service.product_dao, 'update') as mock_update:
            service.update_product(update_data)
            mock_update.assert_called_once()
            updated_product = mock_update.call_args[0][0]
            assert updated_product.name == "Producto Actualizado"
            assert updated_product.unit_measure == "caja"
            assert updated_product.unit_price == 25.99