from unittest.mock import patch

from inventory.services.inventory_service import InventoryService


def test_location_transfer_procedure():
    with patch("inventory.database.Database.call_procedure") as mock_proc:
        # Simular llamada al procedimiento transfer_stock
        InventoryService.transfer_stock(
            product_id=1,
            from_location=1,
            to_location=2,
            quantity=5,
            user_id=1
        )
        
        # Verificar que se llamó al procedimiento correcto
        mock_proc.assert_called_once_with(
            "transfer_stock",
            (1, 1, 2, 5.0, 1, None)
        )