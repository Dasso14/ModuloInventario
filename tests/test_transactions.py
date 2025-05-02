from inventory.models.product import Product
from inventory.utils.database import engine

def test_inventory_transaction():
    db = SessionLocal()
    
    # Crear producto de prueba
    test_product = Product(sku="TEST-TRX", name="Test Transacción", unit_measure="unidad")
    db.add(test_product)
    db.commit()
    
    # Realizar transacción
    repo = InventoryRepository(db)
    transaction = repo.create_transaction(
        product_id=test_product.product_id,
        location_id=1,
        quantity=10,
        transaction_type="entrada"
    )
    
    # Verificaciones
    assert transaction.transaction_id is not None
    assert transaction.quantity == 10
    
    # Limpieza
    db.delete(transaction)
    db.delete(test_product)
    db.commit()
    db.close()