from unittest.mock import patch

import pytest
from inventory.models.product import Product
from inventory.models.transaction import Transaction


def test_transaction_stock_limits():
    # Configurar producto con stock mínimo/máximo
    product = Product(
        product_id=1,
        min_stock=5,
        max_stock=20,
        current_stock=10,
        unit_measure="unidad"
    )
    
    # Mockear el trigger de actualización de stock
    with patch("inventory.database.Database.execute") as mock_db:
        # Transacción válida de entrada
        valid_in = Transaction(
            product_id=1,
            location_id=1,
            quantity=5,
            transaction_type="entrada",  # Usando el enum correcto
            user_id=1
        )
        valid_in.apply_to_product(product)
        assert product.current_stock == 15
        
        # Transacción inválida (sobrepasar máximo)
        invalid_in = Transaction(
            product_id=1,
            location_id=1,
            quantity=10,  # 15 + 10 = 25 > 20 (máximo)
            transaction_type="entrada",
            user_id=1
        )
        with pytest.raises(InventoryOverflowError):
            invalid_in.apply_to_product(product)
        
        # Transacción de ajuste
        adjustment = Transaction(
            product_id=1,
            location_id=1,
            quantity=3,
            transaction_type="ajuste",  # Tipo adicional del enum
            user_id=1
        )
        adjustment.apply_to_product(product)
        assert product.current_stock == 3  # Ajuste sobrescribe el valor