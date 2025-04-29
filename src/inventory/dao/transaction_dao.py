from inventory.database import Database
from inventory.models.transaction import Transaction

class TransactionDAO:
    @staticmethod
    def get_current_stock(product_id: int, location_id: int) -> float:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN transaction_type = 'in' THEN quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN transaction_type = 'out' THEN quantity ELSE 0 END), 0)
                FROM transactions
                WHERE product_id = %s AND location_id = %s
            """, (product_id, location_id))
            result = cursor.fetchone()
            return result[0] if result else 0.0
