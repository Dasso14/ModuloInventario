import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone # Import timezone

from flask import Flask

# Import your blueprint and necessary components
# Assuming the structure allows importing from app.api.transfers
from app.api.transfers import transfers_bp, transfer_service, validate_int_param, validate_date_param

# Import the actual service class for patching if needed, but patching instance is better here
# from app.services import TransferService

from app.utils.exceptions import NotFoundException, ConflictException, InsufficientStockException, DatabaseException

# --- Fixtures ---
@pytest.fixture
def test_client():
    app = Flask(__name__)
    # Register the blueprint directly
    app.register_blueprint(transfers_bp, url_prefix='/api/transfers') # Assuming blueprint is registered at /api/transfers
    with app.test_client() as client:
        yield client

# --- Helper Function Tests ---
# These tests now directly test the helper functions imported from your transfers module
def test_validate_int_param_valid():
    assert validate_int_param("123", "test_param") == 123
    assert validate_int_param(None, "optional_param") is None # Test None handling

def test_validate_int_param_invalid():
    with pytest.raises(ValueError, match="Invalid test_param"):
        validate_int_param("abc", "test_param")
    # Removed the test for None input, as the helper now returns None for None input
    # with pytest.raises(ValueError, match="Invalid test_param"):
    #     validate_int_param(None, "test_param")


def test_validate_date_param_valid():
    # Test with naive datetime input (isoformat without timezone)
    assert validate_date_param("2023-10-27T10:00:00", "test_date") == datetime(2023, 10, 27, 10, 0, 0)

    # Test with timezone-aware datetime input (Z - UTC)
    # fromisoformat returns a timezone-aware datetime for Z or offset
    # The comparison needs to be between timezone-aware datetimes
    assert validate_date_param("2023-10-27T10:00:00Z", "test_date") == datetime(2023, 10, 27, 10, 0, 0, tzinfo=timezone.utc)

    # Test with timezone-aware datetime input (+00:00 offset)
    assert validate_date_param("2023-10-27T10:00:00+00:00", "test_date") == datetime(2023, 10, 27, 10, 0, 0, tzinfo=timezone.utc)

    assert validate_date_param(None, "optional_date") is None # Test None handling


def test_validate_date_param_invalid():
    with pytest.raises(ValueError, match="Invalid test_date format"):
        validate_date_param("2023-10-27T", "test_date")
    with pytest.raises(ValueError, match="Invalid test_date format"):
        validate_date_param("2023/10/27", "test_date")
    with pytest.raises(ValueError, match="Invalid test_date format"):
        validate_date_param("abc", "test_date")
    # Removed the test for None input
    # with pytest.raises(ValueError, match="Invalid test_date format"):
    #     validate_date_param(None, "test_date")


# --- create_transfer() Tests ---
# Refactored test for invalid JSON to send None
def test_create_transfer_invalid_json(test_client):
    # Sending None will trigger the 'if not isinstance(data, dict)' check
    response = test_client.post(
        '/api/transfers/',
        json=None, # Send a null JSON value
        content_type='application/json'
    )
    assert response.status_code == 400
    # The error message matches the code's response for invalid JSON
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}

def test_create_transfer_missing_fields(test_client):
    # Missing 'quantity'
    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'user_id': 1
    })
    assert response.status_code == 400
    # Updated assertion message
    assert response.json == {'success': False, 'message': 'Missing or null required field: quantity'}

    # Missing 'product_id'
    response = test_client.post('/api/transfers/', json={
        'quantity': 10,
        'from_location_id': 1,
        'to_location_id': 2,
        'user_id': 1
    })
    assert response.status_code == 400
    # Updated assertion message
    assert response.json == {'success': False, 'message': 'Missing or null required field: product_id'}

    # Test with a required field being explicitly null
    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': None # Null user_id
    })
    assert response.status_code == 400
    # Updated assertion message
    assert response.json == {'success': False, 'message': 'Missing or null required field: user_id'}


def test_create_transfer_invalid_quantity(test_client):
    # Non-numeric quantity
    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': "abc", # Invalid number string
        'user_id': 1
    })
    assert response.status_code == 400
    # Updated assertion message
    assert response.json == {'success': False, 'message': 'Quantity must be a valid number'}

    # Null quantity - this is now caught by the 'Missing or null required field' check first
    # This test case might become redundant if quantity is always required and checked for null first.
    # However, let's keep the assertion here and ensure the message matches the check that *is* hit.
    # The 'Missing or null required field: quantity' check is hit before the float conversion.
    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': None, # Explicitly null quantity
        'user_id': 1
    })
    assert response.status_code == 400
    # Updated assertion message to match the required_fields check
    assert response.json == {'success': False, 'message': 'Missing or null required field: quantity'}


# Refactored tests to patch only the create_transfer method on the module-level instance
@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_not_found_product(mock_create_transfer, test_client):
    # Simulate the service raising NotFoundException
    mock_create_transfer.side_effect = NotFoundException("Product not found")

    response = test_client.post('/api/transfers/', json={
        'product_id': 999, # Data doesn't matter, mock controls outcome
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 1
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}


@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_not_found_location(mock_create_transfer, test_client):
    # Simulate the service raising NotFoundException (could be from or to location)
    mock_create_transfer.side_effect = NotFoundException("Location not found")

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 999, # Data doesn't matter
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 1
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 999, # Data doesn't matter
        'quantity': 10,
        'user_id': 1
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}


@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_not_found_user(mock_create_transfer, test_client):
    # Simulate the service raising NotFoundException for the user
    mock_create_transfer.side_effect = NotFoundException("User not found")

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 999 # Data doesn't matter
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'User not found'}


@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_insufficient_stock(mock_create_transfer, test_client):
    # Simulate the service raising InsufficientStockException
    mock_create_transfer.side_effect = InsufficientStockException("Insufficient stock in the source location.")

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10, # Data doesn't matter
        'user_id': 1
    })
    assert response.status_code == 409 # Insufficient stock correctly mapped to 409
    assert response.json == {'success': False, 'message': 'Insufficient stock in the source location.'}


@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_success(mock_create_transfer, test_client):
    # Simulate the service successfully creating and returning a transfer object
    mock_transfer_obj = MagicMock(id=123, to_dict=lambda: {'id': 123, 'product_id': 1, 'from_location_id': 1, 'to_location_id': 2, 'quantity': 10.0, 'user_id': 1, 'notes': 'test note'})
    mock_create_transfer.return_value = mock_transfer_obj

    transfer_data = {
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10, # Input can be int/float, API converts to float
        'user_id': 1,
        'notes': 'test note'
    }
    response = test_client.post('/api/transfers/', json=transfer_data)

    # Assert the service method was called with the correct data (quantity is float)
    expected_data_for_service = transfer_data.copy()
    expected_data_for_service['quantity'] = 10.0 # Expect float quantity
    mock_create_transfer.assert_called_once_with(expected_data_for_service)


    assert response.status_code == 201
    assert response.json == {
        'success': True,
        'message': 'Transfer registered successfully',
        'transfer_id': 123,
        'data': mock_transfer_obj.to_dict() # Use the dict from the mock object
    }


@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_database_error(mock_create_transfer, test_client):
    # Simulate the service raising a DatabaseException
    mock_create_transfer.side_effect = DatabaseException("Database error")

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 1,
        'notes': 'test note'
    })
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'Database error'}


# --- list_transfers() Tests ---
# Corrected patching path to target the module-level instance
@patch('app.api.transfers.transfer_service.get_all_transfers')
def test_list_transfers_no_filters(mock_get_all, test_client):
    # Simulate service returning an empty list
    mock_get_all.return_value = []
    response = test_client.get('/api/transfers/')

    # Assert the service method was called with empty dictionaries
    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})

    assert response.status_code == 200
    assert response.json == {'success': True, 'data': []}



# Corrected patching path to target the module-level instance
@patch('app.api.transfers.transfer_service.get_all_transfers')
def test_list_transfers_database_error(mock_get_all, test_client):
    # Simulate service raising a DatabaseException
    mock_get_all.side_effect = DatabaseException("DB error")
    response = test_client.get('/api/transfers/')
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}


# --- get_transfer() Tests ---
# Corrected patching path to target the module-level instance
@patch('app.api.transfers.transfer_service.get_transfer_by_id')
def test_get_transfer_by_id_success(mock_get_transfer, test_client):
    # Simulate service returning a mock transfer object
    mock_transfer_obj = MagicMock(to_dict=lambda: {'id': 1, 'product_id': 1, 'from_location_id': 1, 'to_location_id': 2, 'quantity': 10.0, 'user_id': 1})
    mock_get_transfer.return_value = mock_transfer_obj

    response = test_client.get('/api/transfers/1')

    # Assert service method was called with the correct ID
    mock_get_transfer.assert_called_once_with(1)

    assert response.status_code == 200
    assert response.json == {'success': True, 'data': mock_transfer_obj.to_dict()}


# Corrected patching path to target the module-level instance
@patch('app.api.transfers.transfer_service.get_transfer_by_id')
def test_get_transfer_by_id_not_found(mock_get_transfer, test_client):
    # Simulate service raising NotFoundException
    mock_get_transfer.side_effect = NotFoundException("Transfer not found")

    response = test_client.get('/api/transfers/999')

    # Assert service method was called with the correct ID
    mock_get_transfer.assert_called_once_with(999)

    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Transfer not found'}


# Corrected patching path to target the module-level instance
@patch('app.api.transfers.transfer_service.get_transfer_by_id')
def test_get_transfer_by_id_database_error(mock_get_transfer, test_client):
    # Simulate service raising DatabaseException
    mock_get_transfer.side_effect = DatabaseException("DB error")

    response = test_client.get('/api/transfers/1')

    # Assert service method was called with the correct ID
    mock_get_transfer.assert_called_once_with(1)

    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}


# Primero, añade un mock para la función delete_transfer en TransferService
@patch('app.api.transfers.transfer_service.delete_transfer')
def test_delete_non_existent_transfer(mock_delete_transfer, test_client):
    """TC20: Test deleting a non-existent transfer."""
    # Simular que el servicio lanza NotFoundException
    mock_delete_transfer.side_effect = NotFoundException("Transfer not found")
    non_existent_id = 999999

    response = test_client.delete(f'/api/transfers/{non_existent_id}')

    mock_delete_transfer.assert_called_once_with(non_existent_id)
    assert response.status_code == 404
    # La aserción debe verificar el contenido JSON esperado
    assert response.json == {'success': False, 'message': 'Transfer not found'}
    assert response.headers['Content-Type'] == 'application/json'


# Primero, añade un mock para la función update_transfer en TransferService
@patch('app.api.transfers.transfer_service.update_transfer')
def test_update_non_existent_transfer(mock_update_transfer, test_client):
    """TC21: Test updating a non-existent transfer."""
    # Simular que el servicio lanza NotFoundException
    mock_update_transfer.side_effect = NotFoundException("Transfer not found")
    non_existent_id = 999999
    update_data = {
        "product_id": 1,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": 5.0,
        "user_id": 1
    }

    response = test_client.put(f'/api/transfers/{non_existent_id}', json=update_data)

    mock_update_transfer.assert_called_once_with(non_existent_id, update_data)
    assert response.status_code == 404
    # La aserción debe verificar el contenido JSON esperado
    assert response.json == {'success': False, 'message': 'Transfer not found'}
    assert response.headers['Content-Type'] == 'application/json'