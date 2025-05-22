import pytest
import json
from unittest.mock import MagicMock, patch

from flask import Flask

# Import your blueprint and the service instance
# Adjust the import path based on your project structure
from app.api.reports import reports_bp, report_service

# Import exceptions
from app.utils.exceptions import DatabaseException

# --- Fixtures ---
@pytest.fixture
def app():
    """Fixture for Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'testing' # Needed for some Flask extensions if used
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    return app

@pytest.fixture
def client(app):
    """Fixture for Flask test client."""
    return app.test_client()

# --- Mock Objects ---

# Mock class for list reports (stock levels, low stock, transactions, transfers)
class MockReportItem:
    """Helper mock class for items in list reports."""
    def __init__(self, id, name=None, value=None, **kwargs):
        self.id = id
        self.name = name
        self.value = value
        self.__dict__.update(kwargs) # Allow arbitrary attributes

    def to_dict(self):
        # Return a dictionary representation of the mock object
        # Include common attributes and any extra kwargs
        data = {'id': self.id}
        if self.name is not None:
            data['name'] = self.name
        if self.value is not None:
            data['value'] = self.value
        # Include other specific attributes if needed for a report type
        # For simplicity, we'll add some common ones. Adjust as per your actual service returns.
        if hasattr(self, 'product_id'): data['product_id'] = self.product_id
        if hasattr(self, 'location_id'): data['location_id'] = self.location_id
        if hasattr(self, 'quantity'): data['quantity'] = self.quantity
        if hasattr(self, 'timestamp'): data['timestamp'] = self.timestamp
        if hasattr(self, 'transaction_type'): data['transaction_type'] = self.transaction_type
        if hasattr(self, 'from_location_id'): data['from_location_id'] = self.from_location_id
        if hasattr(self, 'to_location_id'): data['to_location_id'] = self.to_location_id


        return data


def test_get_stock_levels_options(client):
    """Test OPTIONS request to get_stock_levels."""
    response = client.options('/api/reports/stock-levels')
    assert response.status_code == 200
    # Body might be empty or {}, depending on Flask/CORS setup. Check JSON parseable empty or empty dict.
    try:
        assert response.json == {}
    except json.JSONDecodeError:
        assert response.data == b'' # Check for empty byte string


@patch('app.api.reports.report_service.get_stock_levels')
def test_get_stock_levels_database_error(mock_get_stock_levels, client):
    """Test getting stock levels handles database errors."""
    mock_get_stock_levels.side_effect = DatabaseException("Stock DB Error")

    response = client.get('/api/reports/stock-levels')

    mock_get_stock_levels.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred while fetching stock levels.'} # Check exact message


@patch('app.api.reports.report_service.get_stock_levels')
def test_get_stock_levels_unexpected_error(mock_get_stock_levels, client):
    """Test getting stock levels handles unexpected errors."""
    mock_get_stock_levels.side_effect = Exception("Unexpected stock error")

    response = client.get('/api/reports/stock-levels')

    mock_get_stock_levels.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred while fetching stock levels.'} # Check exact message



def test_get_low_stock_report_options(client):
    """Test OPTIONS request to get_low_stock_report."""
    response = client.options('/api/reports/low-stock')
    assert response.status_code == 200
    try:
        assert response.json == {}
    except json.JSONDecodeError:
        assert response.data == b''


@patch('app.api.reports.report_service.get_low_stock_items')
def test_get_low_stock_report_database_error(mock_get_low_stock, client):
    """Test getting low stock report handles database errors."""
    mock_get_low_stock.side_effect = DatabaseException("Low Stock DB Error")

    response = client.get('/api/reports/low-stock')

    mock_get_low_stock.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred while fetching low stock report.'}


@patch('app.api.reports.report_service.get_low_stock_items')
def test_get_low_stock_report_unexpected_error(mock_get_low_stock, client):
    """Test getting low stock report handles unexpected errors."""
    mock_get_low_stock.side_effect = Exception("Unexpected low stock error")

    response = client.get('/api/reports/low-stock')

    mock_get_low_stock.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred while fetching low stock report.'}



def test_get_transaction_history_options(client):
    """Test OPTIONS request to get_transaction_history."""
    response = client.options('/api/reports/transactions')
    assert response.status_code == 200
    try:
        assert response.json == {}
    except json.JSONDecodeError:
        assert response.data == b''


@patch('app.api.reports.report_service.get_transaction_history')
def test_get_transaction_history_database_error(mock_get_history, client):
    """Test getting transaction history handles database errors."""
    mock_get_history.side_effect = DatabaseException("History DB Error")

    response = client.get('/api/reports/transactions')

    mock_get_history.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred while fetching transaction history.'}


@patch('app.api.reports.report_service.get_transaction_history')
def test_get_transaction_history_unexpected_error(mock_get_history, client):
    """Test getting transaction history handles unexpected errors."""
    mock_get_history.side_effect = Exception("Unexpected history error")

    response = client.get('/api/reports/transactions')

    mock_get_history.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred while fetching transaction history.'}



def test_get_transfer_history_options(client):
    """Test OPTIONS request to get_transfer_history."""
    response = client.options('/api/reports/transfers')
    assert response.status_code == 200
    try:
        assert response.json == {}
    except json.JSONDecodeError:
        assert response.data == b''


@patch('app.api.reports.report_service.get_transfer_history')
def test_get_transfer_history_database_error(mock_get_history, client):
    """Test getting transfer history handles database errors."""
    mock_get_history.side_effect = DatabaseException("Transfer DB Error")

    response = client.get('/api/reports/transfers')

    mock_get_history.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred while fetching transfer history.'}


@patch('app.api.reports.report_service.get_transfer_history')
def test_get_transfer_history_unexpected_error(mock_get_history, client):
    """Test getting transfer history handles unexpected errors."""
    mock_get_history.side_effect = Exception("Unexpected transfer error")

    response = client.get('/api/reports/transfers')

    mock_get_history.assert_called_once_with()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred while fetching transfer history.'}


# --- GET /api/reports/total-value Tests ---
@patch('app.api.reports.report_service.get_inventory_total_value')
def test_get_total_inventory_value_success(mock_get_total_value, client):
    """Test getting total inventory value successfully."""
    mock_value = 12345.67
    mock_get_total_value.return_value = mock_value

    response = client.get('/api/reports/total-value')

    # Assert the service method was called with no parameters
    mock_get_total_value.assert_called_once_with()

    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'data': {'total_value': mock_value} # API wraps the scalar value
    }

def test_get_total_inventory_value_options(client):
    """Test OPTIONS request to get_total_inventory_value."""
    response = client.options('/api/reports/total-value')
    assert response.status_code == 200
    try:
        assert response.json == {}
    except json.JSONDecodeError:
        assert response.data == b''


@patch('app.api.reports.report_service.get_inventory_total_value')
def test_get_total_inventory_value_database_error(mock_get_total_value, client):
    """Test getting total inventory value handles database errors."""
    mock_get_total_value.side_effect = DatabaseException("Total Value DB Error")

    response = client.get('/api/reports/total-value')

    mock_get_total_value.assert_called_once_with()
    # Check the specific error message from the API route
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Total Value DB Error'} # Check exact message


@patch('app.api.reports.report_service.get_inventory_total_value')
def test_get_total_inventory_value_unexpected_error(mock_get_total_value, client):
    """Test getting total inventory value handles unexpected errors."""
    mock_get_total_value.side_effect = Exception("Unexpected total value error")

    response = client.get('/api/reports/total-value')

    mock_get_total_value.assert_called_once_with()
    # Check the specific error message from the API route
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred.'} # Check exact message