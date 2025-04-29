from inventory.database import Database
from inventory.models.product import Product

class ProductDAO:
    @staticmethod
    def create(product: Product) -> int:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO products (
                    sku, name, description, category_id, supplier_id,
                    unit_cost, unit_price, unit_measure, weight, volume,
                    min_stock, max_stock, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING product_id
            """, (
                product.sku,
                product.name,
                product.description,
                product.category_id,
                product.supplier_id,
                product.unit_cost,
                product.unit_price,
                product.unit_measure,
                product.weight,
                product.volume,
                product.min_stock,
                product.max_stock,
                product.is_active
            ))
            return cursor.fetchone()[0]

    @staticmethod
    def get_by_id(product_id: int) -> Product:
        with Database.get_cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            row = cursor.fetchone()
            return Product(*row) if row else None