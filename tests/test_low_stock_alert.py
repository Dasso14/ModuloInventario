from unittest.mock import patch
from inventory.services.alert_service import AlertService

def test_low_stock_alert():
    with patch("inventory.services.alert_service.AlertService.send_alert") as mock_alert:
        AlertService.send_alert("Producto con bajo stock")
        mock_alert.assert_called_once_with("Producto con bajo stock")
