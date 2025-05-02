from unittest.mock import patch

import pytest
from inventory.models.product import Product
from inventory.models.transaction import Transaction


def test_transaction_stock_limits():
    product = Product(
        product_id=1,
        min_stock=5,
        max_stock=20,
        current_stock=10,
        unit_measure="unidad"
    )
    
    with patch("inventory.database.Database.execute") as mock_db:
        valid_in = Transaction(
            product_id=1,
            location_id=1,
            quantity=5,
            transaction_type="entrada",  
            user_id=1
        )
        valid_in.apply_to_product(product)
        assert product.current_stock == 15
        
        invalid_in = Transaction(
            product_id=1,
            location_id=1,
            quantity=10,  
            transaction_type="entrada",
            user_id=1
        )
        with pytest.raises(InventoryOverflowError):  # type: ignore
            invalid_in.apply_to_product(product)
        
        adjustment = Transaction(
            product_id=1,
            location_id=1,
            quantity=3,
            transaction_type="ajuste",  
            user_id=1
        )
        adjustment.apply_to_product(product)
        assert product.current_stock == 3  