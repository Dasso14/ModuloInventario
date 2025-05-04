# dao/transaction_dao.py
from inventory.database import Database
from inventory.models.transaction import Transaction


class TransactionDAO:
    @staticmethod
    def create(transaction: Transaction) -> int:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    product_id, location_id, quantity, transaction_type, 
                    user_id, reference_number, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING transaction_id
            """, (
                transaction.product_id,
                transaction.location_id,
                transaction.quantity,
                transaction.transaction_type.value,  # Usar .value del Enum
                transaction.user_id,
                transaction.reference_number,
                transaction.notes
            ))
            return cursor.fetchone()[0]