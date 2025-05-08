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
def test_add_stock_success(mock_create_transaction, test_client):
    """Test adding stock successfully."""
    add_data = {
        'product_id': 1,
        'location_id': 10,
        'quantity': 50.5,
        'user_id': 100,
        'reference_number': 'REF123',
        'notes': 'Initial stock'
    }
    mock_created_transaction = MockTransaction(id=1, transaction_type='add', **add_data)
    mock_create_transaction.return_value = mock_created_transaction

    response = test_client.post('/api/inventory/add', json=add_data)

    # Ensure quantity is passed as float to the service
    expected_service_data = add_data.copy()
    expected_service_data['quantity'] = 50.5
    expected_service_data['transaction_type'] = 'add' # API adds this
    mock_create_transaction.assert_called_once_with(expected_service_data)

    assert response.status_code == 201
    assert response.json == {
        'success': True,
        'message': 'Stock added successfully',
        'transaction_id': 1,
        'data': mock_created_transaction.to_dict()
    }


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