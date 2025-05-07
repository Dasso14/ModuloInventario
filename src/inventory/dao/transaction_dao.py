from psycopg2 import sql, extras
from psycopg2 import DatabaseError
from typing import List
from inventory.utils.database import Database
from inventory.models.transaction import Transaction, TransactionType


class TransactionDAO:
    @staticmethod
    def create(transaction: Transaction) -> int:
        """Crea una transacción individual con manejo de errores transaccionales."""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("BEGIN;")  # Iniciar transacción explícita

                # Insertar transacción
                cursor.execute(
                    sql.SQL("""
                            INSERT INTO inventory_transactions (product_id, location_id, quantity, transaction_type,
                                                                user_id, reference_number, notes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING transaction_id
                            """),
                    (
                        transaction.product_id,
                        transaction.location_id,
                        transaction.quantity,
                        transaction.transaction_type.value,
                        transaction.user_id,
                        transaction.reference_number,
                        transaction.notes
                    )
                )
                transaction_id = cursor.fetchone()[0]
                conn.commit()  # Confirmar transacción
                return transaction_id
        except DatabaseError as e:
            if "serialization" in str(e).lower():  # Detectar error de serialización
                conn.rollback()
                raise RuntimeError("Error de concurrencia: reintentar operación")
            else:
                raise
        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Error en transacción: {str(e)}")
        finally:
            if conn:
                Database.return_connection(conn)

    @staticmethod
    def bulk_insert(transactions: List[Transaction]) -> None:
        """Inserción masiva optimizada usando execute_batch."""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("BEGIN;")

                # Convertir objetos Transaction a tuplas
                data = [
                    (
                        t.product_id,
                        t.location_id,
                        t.quantity,
                        t.transaction_type.value,
                        t.user_id,
                        t.reference_number,
                        t.notes
                    ) for t in transactions
                ]

                # Ejecutar batch de 1000 operaciones por lote
                extras.execute_batch(
                    cursor,
                    """INSERT INTO inventory_transactions (product_id, location_id, quantity, transaction_type,
                                                           user_id, reference_number, notes)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    data,
                    page_size=1000
                )
                conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Error en bulk insert: {str(e)}")
        finally:
            if conn:
                Database.return_connection(conn)

    @staticmethod
    def transfer_stock(
            product_id: int,
            from_location: int,
            to_location: int,
            quantity: float,
            user_id: int
    ) -> None:
        """Transferencia atómica entre ubicaciones con verificación de stock."""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("BEGIN;")

                # 1. Verificar y bloquear stock actual
                cursor.execute(
                    """SELECT quantity
                       FROM stock_levels
                       WHERE product_id = %s
                         AND location_id = %s
                           FOR UPDATE NOWAIT""",
                    (product_id, from_location)
                )
                result = cursor.fetchone()
                if not result or result[0] < quantity:
                    raise ValueError("Stock insuficiente para transferencia")

                # 2. Registrar salida
                cursor.execute(
                    """INSERT INTO inventory_transactions (product_id, location_id, quantity,
                                                           transaction_type, user_id)
                       VALUES (%s, %s, %s, 'salida', %s)""",
                    (product_id, from_location, quantity, user_id)
                )

                # 3. Registrar entrada
                cursor.execute(
                    """INSERT INTO inventory_transactions (product_id, location_id, quantity,
                                                           transaction_type, user_id)
                       VALUES (%s, %s, %s, 'entrada', %s)""",
                    (product_id, to_location, quantity, user_id)
                )

                # 4. Registrar en location_transfers
                cursor.execute(
                    """INSERT INTO location_transfers (product_id, from_location_id, to_location_id,
                                                       quantity, user_id)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (product_id, from_location, to_location, quantity, user_id)
                )

                conn.commit()
        except DatabaseError as e:
            if "serialization" in str(e).lower():  # Detectar error de serialización
                conn.rollback()
                raise RuntimeError("Error de concurrencia: reintentar operación")
            else:
                raise
        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Error en transferencia: {str(e)}")
        finally:
            if conn:
                Database.return_connection(conn)

    @staticmethod
    def get_current_stock(product_id: int, location_id: int) -> float:
        try:
            with Database.get_cursor() as cursor:
                cursor.execute(
                    """SELECT quantity
                       FROM stock_levels
                       WHERE product_id = %s
                         AND location_id = %s""",  # Paréntesis cerrado
                    (product_id, location_id)
                )
                result = cursor.fetchone()
                return result[0] if result else 0.0
        except Exception as e:
            raise RuntimeError(f"Error consultando stock: {str(e)}")