import pytest
import json
import threading
import time
from unittest.mock import MagicMock, patch
from app import create_app

from flask import Flask

# Import your blueprint and the service instance
# Adjust the import path based on your project structure
from app.api.inventory import inventory_bp, inventory_service

# Import exceptions
from app.utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException

@pytest.fixture(scope='module') # Scope to module if app creation is expensive
def app():
    """Fixture for Flask application configured for testing."""
    app_instance = create_app(config_object='config.TestingConfig')
    with app_instance.app_context():
        # If your tests interact with a real (test) database,
        # you might need to create tables here.
        # For unit tests with extensive mocking, this might not be needed
        # if all DB interactions are mocked.
        # db.create_all() # Uncomment if needed
        pass
    yield app_instance
    # with app_instance.app_context():
    # db.drop_all() # Uncomment if you created tables

@pytest.fixture
def test_client(app): # Depends on the 'app' fixture
    """Fixture for Flask test client."""
    return app.test_client()

@pytest.fixture
def runner(app): # For CLI commands if needed
    return app.test_cli_runner()

# --- Fixtures ---
@pytest.fixture
def test_client():
    """Fixture for Flask test client."""
    app = Flask(__name__)
    # Register the blueprint with the correct URL prefix
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    with app.test_client() as client:
        yield client

# --- Mock Objects ---
class MockTransaction:
    """Helper mock class to simulate an InventoryTransaction model object."""
    def __init__(self, id, product_id, location_id, quantity, user_id, transaction_type, reference_number=None, notes=None):
        self.id = id
        self.product_id = product_id
        self.location_id = location_id
        self.quantity = quantity
        self.user_id = user_id
        self.transaction_type = transaction_type
        self.reference_number = reference_number
        self.notes = notes
        # Add timestamp if your model has it
        # self.timestamp = datetime.utcnow()


    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'location_id': self.location_id,
            'quantity': self.quantity,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'reference_number': self.reference_number,
            'notes': self.notes,
            # 'timestamp': self.timestamp.isoformat() if hasattr(self, 'timestamp') else None
        }

class MockTransfer:
    """Helper mock class to simulate a LocationTransfer model object."""
    def __init__(self, id, product_id, from_location_id, to_location_id, quantity, user_id, notes=None):
        self.id = id
        self.product_id = product_id
        self.from_location_id = from_location_id
        self.to_location_id = to_location_id
        self.quantity = quantity
        self.user_id = user_id
        self.notes = notes
        # Add timestamp if your model has it
        # self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'from_location_id': self.from_location_id,
            'to_location_id': self.to_location_id,
            'quantity': self.quantity,
            'user_id': self.user_id,
            'notes': self.notes,
            # 'timestamp': self.timestamp.isoformat() if hasattr(self, 'timestamp') else None
        }
    
class MockStockLevelForConcurrency:
    def __init__(self, product_id, location_id, quantity):
        self.product_id = product_id
        self.location_id = location_id
        self.quantity = quantity
        self.lock = threading.Lock()


# --- POST /api/inventory/add Tests (add_stock) ---

@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_add_stock_missing_required_fields(mock_create_transaction, test_client):
    """Test adding stock with missing required fields."""
    # Missing quantity
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 10, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, location_id, quantity, user_id'} # Checks all required fields


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_add_stock_null_required_fields(mock_create_transaction, test_client):
    """Test adding stock with null values for required fields."""
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': None, 'quantity': 50, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, location_id, quantity, user_id'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_add_stock_invalid_quantity_format(mock_create_transaction, test_client):
    """Test adding stock with invalid quantity format."""
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 10, 'quantity': 'abc', 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid quantity value'}

@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_add_stock_non_positive_quantity(mock_create_transaction, test_client):
    """Test adding stock with non-positive quantity."""
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 10, 'quantity': 0, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be positive for addition'}

    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 10, 'quantity': -10, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be positive for addition'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_add_stock_related_entity_not_found(mock_create_transaction, test_client):
    """Test adding stock when a related entity (product, location, user) is not found."""
    mock_create_transaction.side_effect = NotFoundException("Product not found")
    response = test_client.post('/api/inventory/add', json={
        'product_id': 999, 'location_id': 10, 'quantity': 50, 'user_id': 100
    })
    mock_create_transaction.assert_called_once() # Service is called, raises error
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}

    mock_create_transaction.reset_mock()
    mock_create_transaction.side_effect = NotFoundException("Location not found")
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 999, 'quantity': 50, 'user_id': 100
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}

    mock_create_transaction.reset_mock()
    mock_create_transaction.side_effect = NotFoundException("User not found")
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 10, 'quantity': 50, 'user_id': 999
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'User not found'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_add_stock_database_error(mock_create_transaction, test_client):
    """Test adding stock handles database errors."""
    mock_create_transaction.side_effect = DatabaseException("DB error")
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 10, 'quantity': 50, 'user_id': 100
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred during stock addition'} # Check exact message


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_add_stock_unexpected_error(mock_create_transaction, test_client):
    """Test adding stock handles unexpected errors."""
    mock_create_transaction.side_effect = Exception("Unexpected error")
    response = test_client.post('/api/inventory/add', json={
        'product_id': 1, 'location_id': 10, 'quantity': 50, 'user_id': 100
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}



@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_invalid_json(mock_create_transaction, test_client):
    """Test adjusting stock with invalid JSON data."""
    response = test_client.post(
        '/api/inventory/adjust',
        data='null',
        content_type='application/json'
    )
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_missing_required_fields(mock_create_transaction, test_client):
    """Test adjusting stock with missing required fields."""
    # Missing notes (which is required for adjust)
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 10, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, location_id, quantity, user_id, notes'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_null_required_fields(mock_create_transaction, test_client):
    """Test adjusting stock with null values for required fields."""
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 10, 'user_id': None, 'notes': 'Test'
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, location_id, quantity, user_id, notes'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_empty_notes(mock_create_transaction, test_client):
    """Test adjusting stock with empty or whitespace-only notes."""
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 10, 'user_id': 100, 'notes': ''
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Notes are required for stock adjustments to explain the reason.'}

    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 10, 'user_id': 100, 'notes': '   '
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Notes are required for stock adjustments to explain the reason.'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_invalid_quantity_format(mock_create_transaction, test_client):
    """Test adjusting stock with invalid quantity format."""
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 'xyz', 'user_id': 100, 'notes': 'Test'
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid quantity value'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_zero_quantity(mock_create_transaction, test_client):
    """Test adjusting stock with zero quantity."""
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 0, 'user_id': 100, 'notes': 'Test'
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Adjustment quantity cannot be zero'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_related_entity_not_found(mock_create_transaction, test_client):
    """Test adjusting stock when a related entity is not found."""
    mock_create_transaction.side_effect = NotFoundException("Product not found")
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 999, 'location_id': 10, 'quantity': 10, 'user_id': 100, 'notes': 'Test'
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_insufficient_stock(mock_create_transaction, test_client):
    """Test adjusting stock with a negative quantity that results in insufficient stock."""
    mock_create_transaction.side_effect = InsufficientStockException("Insufficient stock for adjustment")
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': -100, 'user_id': 100, 'notes': 'Test'
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 409 # API maps InsufficientStockException to 409
    assert response.json == {'success': False, 'message': 'Insufficient stock for adjustment'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_database_error(mock_create_transaction, test_client):
    """Test adjusting stock handles database errors."""
    mock_create_transaction.side_effect = DatabaseException("DB error")
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 10, 'user_id': 100, 'notes': 'Test'
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred during stock adjustment'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_unexpected_error(mock_create_transaction, test_client):
    """Test adjusting stock handles unexpected errors."""
    mock_create_transaction.side_effect = Exception("Unexpected error")
    response = test_client.post('/api/inventory/adjust', json={
        'product_id': 1, 'location_id': 10, 'quantity': 10, 'user_id': 100, 'notes': 'Test'
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}



@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_invalid_json(mock_create_transaction, test_client):
    """Test removing stock with invalid JSON data."""
    response = test_client.post(
        '/api/inventory/remove',
        data='null',
        content_type='application/json'
    )
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_missing_required_fields(mock_create_transaction, test_client):
    """Test removing stock with missing required fields."""
    response = test_client.post('/api/inventory/remove', json={
        'product_id': 1, 'location_id': 10, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, location_id, quantity, user_id'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_null_required_fields(mock_create_transaction, test_client):
    """Test removing stock with null values for required fields."""
    response = test_client.post('/api/inventory/remove', json={
        'product_id': None, 'location_id': 10, 'quantity': 5, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, location_id, quantity, user_id'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_invalid_quantity_format(mock_create_transaction, test_client):
    """Test removing stock with invalid quantity format."""
    response = test_client.post('/api/inventory/remove', json={
        'product_id': 1, 'location_id': 10, 'quantity': 'abc', 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid quantity value'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_non_positive_quantity(mock_create_transaction, test_client):
    """Test removing stock with non-positive quantity."""
    response = test_client.post('/api/inventory/remove', json={
        'product_id': 1, 'location_id': 10, 'quantity': 0, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be positive for removal'}

    response = test_client.post('/api/inventory/remove', json={
        'product_id': 1, 'location_id': 10, 'quantity': -10, 'user_id': 100
    })
    mock_create_transaction.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be positive for removal'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_related_entity_not_found(mock_create_transaction, test_client):
    """Test removing stock when a related entity is not found."""
    mock_create_transaction.side_effect = NotFoundException("Product not found")
    response = test_client.post('/api/inventory/remove', json={
        'product_id': 999, 'location_id': 10, 'quantity': 5, 'user_id': 100
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_insufficient_stock(mock_create_transaction, test_client):
    """Test removing stock with quantity greater than available stock."""
    mock_create_transaction.side_effect = InsufficientStockException("Insufficient stock for removal")
    response = test_client.post('/api/inventory/remove', json={
        'product_id': 1, 'location_id': 10, 'quantity': 100, 'user_id': 100
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 409 # API maps InsufficientStockException to 409
    assert response.json == {'success': False, 'message': 'Insufficient stock for removal'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_database_error(mock_create_transaction, test_client):
    """Test removing stock handles database errors."""
    mock_create_transaction.side_effect = DatabaseException("DB error")
    response = test_client.post('/api/inventory/remove', json={
        'product_id': 1, 'location_id': 10, 'quantity': 5, 'user_id': 100
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred during stock removal'}


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_unexpected_error(mock_create_transaction, test_client):
    """Test removing stock handles unexpected errors."""
    mock_create_transaction.side_effect = Exception("Unexpected error")
    response = test_client.post('/api/inventory/remove', json={
        'product_id': 1, 'location_id': 10, 'quantity': 5, 'user_id': 100
    })
    mock_create_transaction.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- POST /api/inventory/transfer Tests (transfer_stock) ---
@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_success(mock_create_transfer, test_client):
    """Test transferring stock successfully."""
    transfer_data = {
        'product_id': 1,
        'from_location_id': 10,
        'to_location_id': 20,
        'quantity': 5.0,
        'user_id': 100,
        'notes': 'Moving stock'
    }
    mock_created_transfer = MockTransfer(id=1, **transfer_data)
    mock_create_transfer.return_value = mock_created_transfer

    response = test_client.post('/api/inventory/transfer', json=transfer_data)

    expected_service_data = transfer_data.copy()
    expected_service_data['quantity'] = 5.0
    mock_create_transfer.assert_called_once_with(expected_service_data)

    assert response.status_code == 201
    assert response.json == {
        'success': True,
        'message': 'Stock transferred successfully',
        'transfer_id': 1,
        'data': mock_created_transfer.to_dict()
    }

@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_invalid_json(mock_create_transfer, test_client):
    """Test transferring stock with invalid JSON data."""
    response = test_client.post(
        '/api/inventory/transfer',
        data='null',
        content_type='application/json'
    )
    mock_create_transfer.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_missing_required_fields(mock_create_transfer, test_client):
    """Test transferring stock with missing required fields."""
    # Missing quantity
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'user_id': 100
    })
    mock_create_transfer.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, from_location_id, to_location_id, quantity, user_id'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_null_required_fields(mock_create_transfer, test_client):
    """Test transferring stock with null values for required fields."""
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 5, 'user_id': None
    })
    mock_create_transfer.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing or null required fields: product_id, from_location_id, to_location_id, quantity, user_id'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_invalid_quantity_format(mock_create_transfer, test_client):
    """Test transferring stock with invalid quantity format."""
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 'abc', 'user_id': 100
    })
    mock_create_transfer.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid quantity value'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_non_positive_quantity(mock_create_transfer, test_client):
    """Test transferring stock with non-positive quantity."""
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 0, 'user_id': 100
    })
    mock_create_transfer.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be positive for transfer'}

    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': -10, 'user_id': 100
    })
    mock_create_transfer.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be positive for transfer'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_same_locations(mock_create_transfer, test_client):
    """Test transferring stock to the same source and destination location."""
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 10, 'quantity': 5, 'user_id': 100
    })
    mock_create_transfer.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Source and destination locations cannot be the same'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_related_entity_not_found(mock_create_transfer, test_client):
    """Test transferring stock when a related entity is not found."""
    mock_create_transfer.side_effect = NotFoundException("Product not found")
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 999, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 5, 'user_id': 100
    })
    mock_create_transfer.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}

    mock_create_transfer.reset_mock()
    mock_create_transfer.side_effect = NotFoundException("Source location not found")
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 999, 'to_location_id': 20, 'quantity': 5, 'user_id': 100
    })
    mock_create_transfer.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Source location not found'}

    mock_create_transfer.reset_mock()
    mock_create_transfer.side_effect = NotFoundException("Destination location not found")
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 999, 'quantity': 5, 'user_id': 100
    })
    mock_create_transfer.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Destination location not found'}

    mock_create_transfer.reset_mock()
    mock_create_transfer.side_effect = NotFoundException("User not found")
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 5, 'user_id': 999
    })
    mock_create_transfer.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'User not found'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_insufficient_stock(mock_create_transfer, test_client):
    """Test transferring stock with quantity greater than available stock at source."""
    mock_create_transfer.side_effect = InsufficientStockException("Insufficient stock at source location")
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 100, 'user_id': 100
    })
    mock_create_transfer.assert_called_once()
    assert response.status_code == 409 # API maps InsufficientStockException to 409
    assert response.json == {'success': False, 'message': 'Insufficient stock at source location'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_database_error(mock_create_transfer, test_client):
    """Test transferring stock handles database errors."""
    mock_create_transfer.side_effect = DatabaseException("DB error")
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 5, 'user_id': 100
    })
    mock_create_transfer.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred during stock transfer'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_unexpected_error(mock_create_transfer, test_client):
    """Test transferring stock handles unexpected errors."""
    mock_create_transfer.side_effect = Exception("Unexpected error")
    response = test_client.post('/api/inventory/transfer', json={
        'product_id': 1, 'from_location_id': 10, 'to_location_id': 20, 'quantity': 5, 'user_id': 100
    })
    mock_create_transfer.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_quantity_greater_than_available(mock_create_transfer, test_client):
    """TC03: Test transferring stock with quantity greater than available stock."""
    # Simular que la excepción InsufficientStockException es lanzada por el servicio
    mock_create_transfer.side_effect = InsufficientStockException("Insufficient stock at source location.")

    transfer_data = {
        "product_id": 1,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": 1000.0, # Cantidad muy grande para simular stock insuficiente
        "user_id": 1
    }
    response = test_client.post(
        '/api/inventory/transfer',
        json=transfer_data
    )

    mock_create_transfer.assert_called_once()
    assert response.status_code == 409 # Esperamos 409 Conflict por stock insuficiente
    assert response.json == {'success': False, 'message': 'Insufficient stock at source location.'}

@patch('app.services.inventory_service.db.session')
@patch('app.services.inventory_service.InventoryService.create_inventory_transaction')
def test_atomic_transfer_rollback_on_destination_failure(mock_create_transaction_for_atomic, mock_db_session, test_client):
    """TC04: Test atomic transfer: rollback on destination update failure."""
    # Mockear las llamadas a create_inventory_transaction para simular el comportamiento deseado.
    # La primera llamada (salida) debería ser exitosa.
    mock_transaction_out = MagicMock(id=10, to_dict=lambda: {'id': 10, 'type': 'salida'})
    # La segunda llamada (entrada) debería ser exitosa, pero simular que el COMMIT posterior falla.
    mock_transaction_in = MagicMock(id=11, to_dict=lambda: {'id': 11, 'type': 'entrada'})

    # Configuramos el mock de create_inventory_transaction para las dos llamadas secuenciales
    mock_create_transaction_for_atomic.side_effect = [
        mock_transaction_out, # Primera llamada para la salida
        mock_transaction_in   # Segunda llamada para la entrada
    ]

    # Simular que el commit final (después de crear ambas transacciones y la transferencia) falla
    mock_db_session.commit.side_effect = Exception("Forced database commit failure on destination update")

    transfer_data = {
        "product_id": 1,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": 5.0,
        "user_id": 1,
        "notes": "Test atomic rollback"
    }

    response = test_client.post(
        '/api/inventory/transfer',
        json=transfer_data
    )

    # Verificamos que se intentó hacer el commit y luego el rollback
    mock_db_session.commit.assert_called_once()
    mock_db_session.rollback.assert_called_once() # Debería haber un rollback

    # Assert the response indicates an internal server error
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error occurred during stock transfer'}

    # Opcional: Puedes añadir aserciones para verificar que se intentó crear ambas transacciones
    assert mock_create_transaction_for_atomic.call_count == 2


@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_remove_stock_results_in_negative_stock(mock_create_transaction, test_client):
    """TC06: Test removing stock that would result in negative stock."""
    # Simular que la excepción InsufficientStockException es lanzada por el servicio
    mock_create_transaction.side_effect = InsufficientStockException("Insufficient stock for removal")

    remove_data = {
        "product_id": 1,
        "location_id": 1,
        "quantity": 1000.0, # Cantidad a remover que excedería el stock
        "user_id": 1,
        "transaction_type": "salida" # Tipo de transacción
    }
    response = test_client.post(
        '/api/inventory/remove',
        json=remove_data
    )

    mock_create_transaction.assert_called_once()
    assert response.status_code == 409 # Esperamos 409 Conflict
    assert response.json == {'success': False, 'message': 'Insufficient stock for removal'}

@patch('app.api.inventory.inventory_service.create_inventory_transaction')
def test_adjust_stock_results_in_negative_stock(mock_create_transaction, test_client):
    """TC06: Test adjusting stock with negative quantity that would result in negative stock."""
    # Simular que la excepción InsufficientStockException es lanzada por el servicio
    mock_create_transaction.side_effect = InsufficientStockException("Adjustment would result in negative stock")

    adjust_data = {
        "product_id": 1,
        "location_id": 1,
        "quantity": -1000.0, # Ajuste negativo que excedería el stock
        "user_id": 1,
        "notes": "Ajuste por pérdida grande",
        "transaction_type": "ajuste" # Tipo de transacción
    }
    response = test_client.post(
        '/api/inventory/adjust',
        json=adjust_data
    )

    mock_create_transaction.assert_called_once()
    assert response.status_code == 409 # Esperamos 409 Conflict
    assert response.json == {'success': False, 'message': 'Adjustment would result in negative stock'}

mock_current_stock = MockStockLevelForConcurrency(product_id=1, location_id=1, quantity=100)

@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_concurrent_transfers(mock_create_transfer, test_client, app):
    """TC09: Test multiple simultaneous transfers for consistency."""
    # Configurar el mock para que simule éxito en la creación de transferencia
    mock_create_transfer.return_value = MagicMock(id=1, to_dict=lambda: {'id': 1, 'product_id': 1, 'from_location_id': 1, 'to_location_id': 2, 'quantity': 5.0, 'user_id': 1})

    num_transfers = 5
    quantity_per_transfer = 5.0
    initial_stock = 100.0
    final_stock_expected = initial_stock - (num_transfers * quantity_per_transfer)

    # Mock del método de obtención de stock para que siempre devuelva el stock inicial simulado
    # Importante: para concurrencia, esto debería ser un mock que se actualice o un DB de test
    # Aquí es un mock simplificado que no simula el cambio de stock intermedio.
    # Un test de concurrencia *real* no mockearía el servicio de esta manera, sino que interactuaría con la DB.
    with patch('app.services.transaction_service.TransactionService._get_current_stock', return_value=initial_stock):
        transfer_data = {
            "product_id": 1,
            "from_location_id": 1,
            "to_location_id": 2,
            "quantity": quantity_per_transfer,
            "user_id": 1,
            "notes": "Concurrent transfer"
        }

        # Lista para guardar los hilos
        threads = []
        results = []
        results_lock = threading.Lock()

        def send_request(data_payload):
            with app.app_context(): # <--- CRITICAL CHANGE: Establish app context
                response = test_client.post('/api/inventory/transfer', json=data_payload)
                with results_lock:
                    results.append(response)

        # Crear y lanzar hilos
        for _ in range(num_transfers):
            thread = threading.Thread(target=send_request, args=(transfer_data,))
            threads.append(thread)
            thread.start()

        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()

        # Validar resultados
        success_count = 0
        for res in results:
            assert res.status_code == 201 # O el código que el API retorne en éxito
            assert res.json['success'] is True
            success_count += 1

        assert success_count == num_transfers
        # En un test real de integración, aquí se consultaría el stock final de la DB
        # y se compararía con final_stock_expected.
        # Por ahora, dado el mock del servicio, solo podemos confirmar que todas las llamadas al servicio fueron exitosas.
        assert mock_create_transfer.call_count == num_transfers

@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_same_source_and_destination(mock_create_transfer, test_client):
    """TC19: Test creating a transfer with the same source and destination locations."""
    # The service method ValueError is not needed for this specific API validation test
    # mock_create_transfer.side_effect = ValueError("Source and destination locations cannot be the same")

    transfer_data = {
        "product_id": 1,
        "from_location_id": 1,
        "to_location_id": 1, # Mismo origen y destino
        "quantity": 5.0,
        "user_id": 1
    }
    response = test_client.post(
        '/api/inventory/transfer',
        json=transfer_data
    )

    mock_create_transfer.assert_not_called() # <--- MODIFIED ASSERTION
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Source and destination locations cannot be the same'}


@patch('app.api.inventory.inventory_service.create_location_transfer')
def test_transfer_stock_negative_quantity(mock_create_transfer, test_client):
    """TC22: Test creating a transfer with a negative quantity."""
    # Simular que el servicio lanza una excepción por cantidad negativa
    mock_create_transfer.side_effect = ValueError("Transfer quantity must be positive.")

    transfer_data = {
        "product_id": 1,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": -5.0, # Cantidad negativa
        "user_id": 1
    }
    response = test_client.post(
        '/api/inventory/transfer',
        json=transfer_data
    )

    mock_create_transfer.assert_not_called() # MODIFIED
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be positive for transfer'}