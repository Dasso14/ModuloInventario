from inventory.database import Database
from inventory.models.product import Product
from datetime import datetime

class ProductDAO:
    @staticmethod
    def create(product: Product) -> int:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO products (
                    sku, name, description, category_id, supplier_id,
                    unit_cost, unit_price, unit_measure, weight, volume,
                    min_stock, max_stock, is_active, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                product.is_active,
                product.created_at,
                product.updated_at
            ))
            return cursor.fetchone()[0]

    @staticmethod
    def get_by_id(product_id: int) -> Product:
        with Database.get_cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))
                return Product(**data)
            return None

    @staticmethod
    def update(product: Product) -> None:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                UPDATE products SET
                    sku = %s,
                    name = %s,
                    description = %s,
                    category_id = %s,
                    supplier_id = %s,
                    unit_cost = %s,
                    unit_price = %s,
                    unit_measure = %s,
                    weight = %s,
                    volume = %s,
                    min_stock = %s,
                    max_stock = %s,
                    is_active = %s,
                    updated_at = %s
                WHERE product_id = %s
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
                product.is_active,
                product.updated_at,
                product.product_id
            ))

    @staticmethod
    def delete(product_id: int) -> None:
        with Database.get_cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
