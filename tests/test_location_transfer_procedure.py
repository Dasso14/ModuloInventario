from unittest.mock import patch

def test_location_transfer_procedure():
    with patch("inventory.database.Database.call_procedure") as mock_proc:
        mock_proc.return_value = None
        from inventory.database import Database
        Database.call_procedure("transfer_product", args=(1, 2, 10))
        mock_proc.assert_called_once_with("transfer_product", args=(1, 2, 10))
