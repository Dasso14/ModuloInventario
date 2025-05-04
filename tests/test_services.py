from inventory.services.inventory_service import InventoryService
from inventory.utils.database import Database

def test_add_product_with_mock_data():
    Database.initialize()
    service = InventoryService()
    
    data = {
        "product_id": 0,
        "sku": "TEST-001",
        "name": "Teclado",
        "description": "Teclado mecánico",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 20.0,
        "unit_price": 40.0,
        "unit_measure": "unidad",
        "weight": 0.8,
        "volume": 0.02,
        "min_stock": 5,
        "max_stock": 50,
        "is_active": True,
        "created_at": __import__('datetime').datetime.now(),
        "updated_at": __import__('datetime').datetime.now(),
    }

    try:
        product_id = service.add_product(data)
        assert isinstance(product_id, int)
    except Exception:
        assert False, "Falló al agregar producto válido"
