from inventory.dao.product_dao import ProductDAO
from inventory.dao.transaction_dao import TransactionDAO

class InventoryService:
    def __init__(self):
        self.product_dao = ProductDAO()
        self.transaction_dao = TransactionDAO()

    def add_product(self, product_data: dict):
        # Validaciones de negocio
        if not self._validate_product_data(product_data):
            raise ValueError("Invalid product data")
        
        product = Product(**product_data)
        return self.product_dao.create(product)

    def get_product_stock(self, product_id: int, location_id: int) -> float:
        return self.transaction_dao.get_current_stock(product_id, location_id)

    def _validate_product_data(self, product_data: dict) -> bool:
        # Implementar lógica de validación
        return True