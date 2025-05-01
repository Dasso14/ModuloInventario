import pytest
from inventory.services.inventory_service import InventoryService
from inventory.models.product import Product
from datetime import datetime

def test_inventory_service_add_product():
    service = InventoryService()
    
    valid_product_data = {
        "product_id": 0,
        "sku": "VALID-001",
        "name": "Producto válido",
        "description": "Descripción válida",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 15.0,
        "unit_price": 30.0,
        "unit_measure": "unidad",
        "weight": 1.0,
        "volume": 0.05,
        "min_stock": 2,
        "max_stock": 20,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    product_id = service.add_product(valid_product_data)
    assert isinstance(product_id, int)
    
    invalid_product_data = valid_product_data.copy()
    invalid_product_data["sku"] = "INVALIDO"
    
    with pytest.raises(ValueError):
        service.add_product(invalid_product_data)