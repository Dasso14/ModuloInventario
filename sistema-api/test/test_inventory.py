import pytest
import json
from unittest.mock import MagicMock, patch

from flask import Flask

# Import your blueprint and the service instance
# Adjust the import path based on your project structure
from app.api.inventory import inventory_bp, inventory_service

# Import exceptions
from app.utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException

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
def test_atomicity_transfer_reverts_on_destination_failure(client, monkeypatch): # Usando monkeypatch como en el original
    # Paso 1: Crear producto y ubicaciones, y añadir stock inicial
    loc_A_resp = client.post('/api/locations/', json={"name": "Almacen A TC04"})
    assert loc_A_resp.status_code in (201, 409)
    loc_A_id = loc_A_resp.get_json().get("location_id") if loc_A_resp.status_code != 409 else client.get('/api/locations/?name=Almacen A TC04').get_json()['data'][0]['id']

    loc_B_resp = client.post('/api/locations/', json={"name": "Almacen B TC04"})
    assert loc_B_resp.status_code in (201, 409)
    loc_B_id = loc_B_resp.get_json().get("location_id") if loc_B_resp.status_code != 409 else client.get('/api/locations/?name=Almacen B TC04').get_json()['data'][0]['id']

    product_payload = {
        "sku": "TC04_PROD_ATOMIC",
        "name": "Producto Atomic TC04",
        "category_id": 1, # Asume que existe
        "supplier_id": 1, # Asume que existe
        "unit_cost": 50.0,
        "unit_price": 100.0
    }
    product_resp = client.post('/api/products/', json=product_payload)
    assert product_resp.status_code in (200, 201), f"Falló la creación de producto: {product_resp.get_data(as_text=True)}"
    product_id = product_resp.get_json()["data"]["id"]

    add_stock_payload = {
        "product_id": product_id,
        "location_id": loc_A_id,
        "quantity": 10,
        "user_id": 1 # Asume que existe
    }
    add_stock_resp = client.post('/api/inventory/add', json=add_stock_payload)
    assert add_stock_resp.status_code == 201, f"Falló al añadir stock: {add_stock_resp.get_data(as_text=True)}"

    initial_stock_loc_A_resp = client.get(f'/api/products/{product_id}/stock-levels')
    initial_stock_loc_A_data = next(sl for sl in initial_stock_loc_A_resp.get_json()['data'] if sl['location_id'] == loc_A_id)
    initial_stock_A_val = float(initial_stock_loc_A_data['quantity'])
    assert initial_stock_A_val == 10

    # Simular que la segunda parte de la transferencia (actualizar stock en destino) falla
    # Esto depende de cómo esté implementado tu InventoryService.create_location_transfer
    # Si create_location_transfer llama a create_inventory_transaction dos veces,
    # puedes parchear la segunda llamada a create_inventory_transaction o la lógica
    # interna que actualiza el stock_level en el destino.

    # Ejemplo de parcheo conceptual:
    # Aquí monkeypatch se usa sobre 'app.services.inventory_service.InventoryService.create_inventory_transaction'
    # pero necesitas una forma más granular de hacer que solo la *segunda* llamada (la de destino) falle.
    # Una forma podría ser usar un contador o verificar los argumentos de la llamada.
    
    # Para una prueba más directa de la atomicidad en el servicio,
    # sería mejor una prueba unitaria del servicio `create_location_transfer`
    # donde puedas controlar el comportamiento de sus dependencias (como db.session.commit o sub-llamadas).
    
    # Aquí intentamos simularlo a nivel de API, lo cual es más complejo.
    # Este es el fragmento del test original, el resto falta.
    # El objetivo es verificar que si la adición al destino falla, la sustracción del origen se revierte.
    
    # NOTA: El test original está incompleto. Se necesita el mockeo específico.
    # Aquí se asume que el servicio InventoryService es importado y su método
    # create_inventory_transaction es llamado internamente por create_location_transfer.
    # Vamos a parchear create_inventory_transaction para que la segunda llamada (al destino) falle.

    from app.services import InventoryService # Asegúrate que esto sea importable en el contexto del test

    original_create_transaction = InventoryService.create_inventory_transaction
    call_count = 0

    def mock_create_transaction_fails_on_destination(self_service, data):
        nonlocal call_count
        call_count += 1
        if data['transaction_type'] == 'transferencia_destino' or (call_count > 1 and data['location_id'] == loc_B_id) : # Asumiendo que la segunda llamada es para destino
            raise Exception("Simulated failure on destination stock update")
        return original_create_transaction(self_service, data)

    monkeypatch.setattr(InventoryService, 'create_inventory_transaction', mock_create_transaction_fails_on_destination)

    transfer_payload = {
        "product_id": product_id,
        "from_location_id": loc_A_id,
        "to_location_id": loc_B_id,
        "quantity": 5,
        "user_id": 1
    }
    
    transfer_resp = client.post('/api/inventory/transfer', json=transfer_payload)

    # Se espera que la transferencia falle debido al error simulado.
    # El código de estado podría ser 500 si el error no se maneja específicamente para revertir.
    assert transfer_resp.status_code == 500, "La transferencia debe fallar si la actualización en destino falla"
    
    # Verificar que el stock en origen (loc_A_id) NO haya cambiado (se revirtió la salida).
    # Es crucial que la sesión de la base de datos se revierta correctamente.
    final_stock_loc_A_resp = client.get(f'/api/products/{product_id}/stock-levels')
    final_stock_loc_A_data = next(sl for sl in final_stock_loc_A_resp.get_json()['data'] if sl['location_id'] == loc_A_id)
    final_stock_A_val = float(final_stock_loc_A_data['quantity'])
    
    assert final_stock_A_val == initial_stock_A_val, "El stock en origen debe revertirse a su estado inicial"

    # Verificar que el stock en destino (loc_B_id) no haya aumentado.
    final_stock_loc_B_resp = client.get(f'/api/products/{product_id}/stock-levels')
    final_stock_loc_B_data = next((sl for sl in final_stock_loc_B_resp.get_json()['data'] if sl['location_id'] == loc_B_id), None)
    final_stock_B_val = float(final_stock_loc_B_data['quantity']) if final_stock_loc_B_data else 0
    
    assert final_stock_B_val == 0, "El stock en destino no debe haber cambiado"

    monkeypatch.undo() # Restaurar el método original
# Archivo: sistema-api/test/test_transfers.py
import threading # Necesario para pruebas de concurrencia

# (Asegúrate de tener fixtures o crear datos necesarios como categorías y proveedores)
def test_concurrent_transfers_no_inconsistency(client):
    # Crear categoría y proveedor si no existen y son requeridos por el modelo de producto
    client.post('/api/categories/', json={"name": "Categoria Concurrencia TC09"})
    client.post('/api/suppliers/', json={"name": "Proveedor Concurrencia TC09"})

    # Crear ubicaciones
    loc_E_resp = client.post('/api/locations/', json={"name": "Almacen E TC09"})
    assert loc_E_resp.status_code in (201, 409)
    loc_E_id = loc_E_resp.get_json().get("location_id") if loc_E_resp.status_code != 409 else client.get('/api/locations/?name=Almacen E TC09').get_json()['data'][0]['id']

    loc_F_resp = client.post('/api/locations/', json={"name": "Almacen F TC09"})
    assert loc_F_resp.status_code in (201, 409)
    loc_F_id = loc_F_resp.get_json().get("location_id") if loc_F_resp.status_code != 409 else client.get('/api/locations/?name=Almacen F TC09').get_json()['data'][0]['id']

    product_payload = {
        "sku": "CONCURRENCY_PROD_TC09",
        "name": "Producto Concurrencia TC09",
        "category_id": 1, # Asume que existe
        "supplier_id": 1, # Asume que existe
        "unit_cost": 100.0,
        "unit_price": 200.0
    }
    product_resp = client.post('/api/products/', json=product_payload) # URL con /
    assert product_resp.status_code in (200, 201), f"Falló la creación de producto: {product_resp.get_data(as_text=True)}"
    product_id = product_resp.get_json()["data"]["id"]

    # Añadir stock inicial suficiente para las transferencias
    add_stock_payload = {
        "product_id": product_id,
        "location_id": loc_E_id,
        "quantity": 100, # Stock inicial
        "user_id": 1 # Asume que existe
    }
    add_stock_resp = client.post('/api/inventory/add', json=add_stock_payload)
    assert add_stock_resp.status_code == 201, f"Falló al añadir stock: {add_stock_resp.get_data(as_text=True)}"

    # ... (resto del test que involucra threads y transferencias)
    # Ejemplo de cómo podrías estructurar la parte concurrente:
    num_transfers = 5
    transfer_amount = 1
    results = []

    def make_transfer():
        payload = {
            "product_id": product_id,
            "from_location_id": loc_E_id,
            "to_location_id": loc_F_id,
            "quantity": transfer_amount,
            "user_id": 1
        }
        resp = client.post('/api/inventory/transfer', json=payload)
        results.append(resp.status_code)

    threads = []
    for _ in range(num_transfers):
        thread = threading.Thread(target=make_transfer)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Verificar resultados: todos deben ser 201 si hay stock suficiente
    # o una mezcla de 201 y 409 si el stock se agota.
    # La clave es que el stock final sea consistente.
    # print(f"Resultados de transferencia concurrente: {results}")
    
    # Verificar stock final
    stock_E_resp = client.get(f'/api/products/{product_id}/stock-levels')
    stock_E_data = next((sl for sl in stock_E_resp.get_json()['data'] if sl['location_id'] == loc_E_id), None)
    stock_E_final = float(stock_E_data['quantity']) if stock_E_data else 0
    
    stock_F_resp = client.get(f'/api/products/{product_id}/stock-levels')
    stock_F_data = next((sl for sl in stock_F_resp.get_json()['data'] if sl['location_id'] == loc_F_id), None)
    stock_F_final = float(stock_F_data['quantity']) if stock_F_data else 0

    successful_transfers = sum(1 for r in results if r == 201)
    
    assert stock_E_final == 100 - (successful_transfers * transfer_amount)
    assert stock_F_final == (successful_transfers * transfer_amount)
    # Esta aserción es simplista; una prueba de concurrencia real podría necesitar
    # verificar la ausencia de race conditions más profundamente (ej. bloqueos, logs).
