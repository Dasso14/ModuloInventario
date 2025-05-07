from unittest.mock import patch
from inventory.services.inventory_service import InventoryService
from inventory.models.product import Product
from datetime import datetime

def test_add_product_with_mock_data():
    service = InventoryService()
    now = datetime.utcnow()
    product_data = {
        "sku": "MOCK123",
        "name": "Producto Mock",
        "description": "Descripción mock",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 5.0,
        "unit_price": 10.0,
        "unit_measure": "unidad",
        "weight": 0.5,
        "volume": 0.2,
        "min_stock": 2,
        "max_stock": 20,
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }

    with patch.object(service.product_dao, 'create', return_value=1) as mock_create:
        product_id = service.add_product(product_data)
        mock_create.assert_called_once()
        assert product_id == 1