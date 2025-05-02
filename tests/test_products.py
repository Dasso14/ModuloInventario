from inventory.models.product import Product
from inventory.utils.database import engine

def test_create_product():
    db = SessionLocal()
    repo = ProductRepository(db)
    
    # Datos de prueba
    product_data = {
        "sku": "TEST-001",
        "name": "Producto de Prueba",
        "unit_measure": "unidad",
        "unit_price": 10.99
    }
    
    # Crear producto
    new_product = repo.create(product_data)
    
    # Verificaciones
    assert new_product.product_id is not None
    assert new_product.sku == "TEST-001"
    assert new_product.unit_price == 10.99
    
    # Limpieza
    db.delete(new_product)
    db.commit()
    db.close()