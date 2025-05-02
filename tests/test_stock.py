from inventory.models.product import Product
from inventory.utils.database import engine

def test_low_stock_alert():
    db = SessionLocal()
    
    # Crear producto con stock mínimo
    test_product = Product(
        sku="LOW-STOCK",
        name="Producto Stock Bajo",
        min_stock=5,
        unit_measure="unidad"
    )
    db.add(test_product)
    db.commit()
    
    # Crear nivel de stock bajo
    stock = StockLevel(
        product_id=test_product.product_id,
        location_id=1,
        quantity=3  # Por debajo del mínimo
    )
    db.add(stock)
    db.commit()
    
    # Verificar alerta
    service = InventoryService(db)
    low_stock_items = service.check_low_stock()
    
    assert any(item.product_id == test_product.product_id for item in low_stock_items)
    
    # Limpieza
    db.delete(stock)
    db.delete(test_product)
    db.commit()
    db.close()