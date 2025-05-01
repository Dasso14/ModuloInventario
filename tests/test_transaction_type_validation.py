from inventory.models.transaction import Transaction
from datetime import datetime

def test_transaction_type_validation():
    valid_transaction = Transaction(
        transaction_id=1,
        product_id=101,
        location_id=1,
        quantity=5.0,
        transaction_type="in",
        transaction_date=datetime.now()
    )
    
    assert valid_transaction.transaction_type in ("in", "out")