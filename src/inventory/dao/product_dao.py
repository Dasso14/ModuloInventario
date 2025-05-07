# product_dao.py
from psycopg2 import sql, extras
from psycopg2 import errors as psycopg2_errors
from typing import List, Optional, Dict
from inventory.utils.database import Database
from inventory.models.product import Product
from datetime import datetime

class DatabaseError(Exception):
    """Base exception para errores de base de datos"""
    pass

class RecordNotFoundError(DatabaseError):
    """Excepción cuando no se encuentra un registro"""
    pass

class DuplicateEntryError(DatabaseError):
    """Excepción para entradas duplicadas"""
    pass

class ProductDAO:
    @staticmethod
    def create(product: Product) -> int:
        """
        Crea un nuevo producto en la base de datos
        Devuelve el ID del producto creado
        """
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO products (
                        sku, name, description, category_id, supplier_id,
                        unit_cost, unit_price, unit_measure, weight, volume,
                        min_stock, max_stock, is_active
                    ) VALUES (
                        %(sku)s, %(name)s, %(description)s, %(category_id)s, %(supplier_id)s,
                        %(unit_cost)s, %(unit_price)s, %(unit_measure)s, %(weight)s, %(volume)s,
                        %(min_stock)s, %(max_stock)s, %(is_active)s
                    )
                    RETURNING product_id
                """, product.__dict__)

                product_id = cursor.fetchone()[0]
                conn.commit()
                return product_id

        except psycopg2_errors.UniqueViolation as e:
            conn.rollback()
            raise DuplicateEntryError(f"SKU duplicado: {product.sku}") from e
        except psycopg2_errors.ForeignKeyViolation as e:
            conn.rollback()
            raise DatabaseError(f"Error de clave foránea: {str(e)}") from e
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Error creando producto: {str(e)}") from e
        finally:
            if conn:
                Database.return_connection(conn)

    @staticmethod
    def get_by_id(product_id: int) -> Optional[Product]:
        """Obtiene un producto por su ID"""
        try:
            with Database.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        product_id, sku, name, description, category_id,
                        supplier_id, unit_cost, unit_price, unit_measure,
                        weight, volume, min_stock, max_stock, is_active,
                        created_at, updated_at
                    FROM products 
                    WHERE product_id = %s
                """, (product_id,))

                result = cursor.fetchone()
                if not result:
                    raise RecordNotFoundError(f"Producto {product_id} no encontrado")

                return Product(*result)

        except Exception as e:
            raise DatabaseError(f"Error obteniendo producto: {str(e)}") from e

    @staticmethod
    def bulk_insert(products: List[Product]) -> None:
        """Inserción masiva optimizada"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("BEGIN;")

                data = [
                    (
                        p.sku, p.name, p.description, p.category_id, p.supplier_id,
                        p.unit_cost, p.unit_price, p.unit_measure, p.weight, p.volume,
                        p.min_stock, p.max_stock, p.is_active
                    ) for p in products
                ]

                extras.execute_values(
                    cursor,
                    """INSERT INTO products (
                        sku, name, description, category_id, supplier_id,
                        unit_cost, unit_price, unit_measure, weight, volume,
                        min_stock, max_stock, is_active
                    ) VALUES %s""",
                    data,
                    page_size=500
                )
                conn.commit()

        except psycopg2_errors.UniqueViolation as e:
            conn.rollback()
            raise DuplicateEntryError("SKU duplicado en inserción masiva") from e
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Error en inserción masiva: {str(e)}") from e
        finally:
            if conn:
                Database.return_connection(conn)

    @staticmethod
    def update(product_id: int, update_data: Dict) -> None:
        """Actualiza un producto existente"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                set_clauses = []
                params = {"product_id": product_id}

                for key in update_data:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = update_data[key]

                query = f"""
                    UPDATE products 
                    SET {', '.join(set_clauses)}
                    WHERE product_id = %(product_id)s
                """

                cursor.execute(query, params)
                if cursor.rowcount == 0:
                    raise RecordNotFoundError(f"Producto {product_id} no encontrado")

                conn.commit()

        except psycopg2_errors.UniqueViolation as e:
            conn.rollback()
            raise DuplicateEntryError("Violación de unicidad en actualización") from e
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Error actualizando producto: {str(e)}") from e
        finally:
            if conn:
                Database.return_connection(conn)

    @staticmethod
    def delete(product_id: int) -> None:
        """Eliminación lógica de un producto"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE products 
                    SET is_active = FALSE 
                    WHERE product_id = %s
                """, (product_id,))

                if cursor.rowcount == 0:
                    raise RecordNotFoundError(f"Producto {product_id} no encontrado")

                conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Error eliminando producto: {str(e)}") from e
        finally:
            if conn:
                Database.return_connection(conn)

    @staticmethod
    def get_low_stock(threshold: float = 0.2) -> List[Product]:
        """Obtiene productos con stock bajo"""
        try:
            with Database.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.product_id, p.sku, p.name, p.description, p.category_id,
                        p.supplier_id, p.unit_cost, p.unit_price, p.unit_measure,
                        p.weight, p.volume, p.min_stock, p.max_stock, p.is_active,
                        p.created_at, p.updated_at
                    FROM stock_levels sl
                    JOIN products p ON p.product_id = sl.product_id
                    WHERE sl.quantity < (p.max_stock * %s)
                """, (threshold,))

                return [Product(*row) for row in cursor.fetchall()]

        except Exception as e:
            raise DatabaseError(f"Error obteniendo bajo stock: {str(e)}") from e
