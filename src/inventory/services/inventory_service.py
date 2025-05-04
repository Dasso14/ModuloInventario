from inventory.dao.product_dao import ProductDAO
from inventory.dao.transaction_dao import TransactionDAO
from inventory.models.product import Product


class InventoryService:
    def __init__(self):
        self.product_dao = ProductDAO()
        self.transaction_dao = TransactionDAO()

    def add_product(self, product_data: dict) -> int:
        if not self._validate_product_data(product_data):
            raise ValueError("Datos de producto inválidos")

        product = Product(**product_data)
        return self.product_dao.create(product)

    @staticmethod
    def _validate_product_data(product_data: dict) -> bool:
        required = ['sku', 'name', 'category_id', 'supplier_id', 'unit_cost', 'unit_price']
        return all(field in product_data for field in required)