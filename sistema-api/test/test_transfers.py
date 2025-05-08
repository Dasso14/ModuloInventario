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

# This test looks mostly correct after fixing helper function and message asserts
@patch('app.api.transfers.transfer_service.get_all_transfers')
def test_list_transfers_with_valid_filters(mock_get_all, test_client):
    # Simulate service returning a list of mock transfer objects
    mock_transfer = MagicMock(to_dict=lambda: {'id': 1, 'product_id': 1, 'from_location_id': 2, 'to_location_id': 3, 'user_id': 4})
    mock_get_all.return_value = [mock_transfer]

    # Note: Query parameters are strings. Dates with Z or offset are timezone-aware.
    response = test_client.get('/api/transfers/?productId=1&fromLocationId=2&toLocationId=3&userId=4&startDate=2023-10-26T10:00:00Z&endDate=2023-10-27T10:00:00+00:00&page=1&limit=10&sortBy=id&order=asc')
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['id'] == 1 # Check data content

    # Assert the service method was called with the correctly parsed parameters
    mock_get_all.assert_called_once_with(filters={
        'product_id': 1, # Should be int
        'from_location_id': 2, # Should be int
        'to_location_id': 3, # Should be int
        'user_id': 4, # Should be int
        # fromisoformat returns timezone-aware datetimes for Z or offset
        'start_date': datetime(2023, 10, 26, 10, 0, 0, tzinfo=timezone.utc),
        'end_date': datetime(2023, 10, 27, 10, 0, 0, tzinfo=timezone.utc)
    }, pagination={'page': 1, 'limit': 10}, sorting={'id': 'asc'})


# Updated assertions for error messages
def test_list_transfers_invalid_parameter_types(test_client):
    response = test_client.get('/api/transfers/?productId=abc')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid productId'}

    response = test_client.get('/api/transfers/?fromLocationId=abc')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid fromLocationId'}

    response = test_client.get('/api/transfers/?toLocationId=abc')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid toLocationId'}

    response = test_client.get('/api/transfers/?userId=abc')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid userId'}

    response = test_client.get('/api/transfers/?startDate=invalid')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid startDate format'}

    response = test_client.get('/api/transfers/?endDate=invalid')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid endDate format'}

    response = test_client.get('/api/transfers/?page=abc')
    assert response.status_code == 400
    # Updated assertion message
    assert response.json == {'success': False, 'message': 'Invalid page'}

    response = test_client.get('/api/transfers/?limit=abc')
    assert response.status_code == 400
    # Updated assertion message
    assert response.json == {'success': False, 'message': 'Invalid limit'}

    # Test basic validation added to helper usage in route
    response = test_client.get('/api/transfers/?page=0')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Page number must be positive'}

    response = test_client.get('/api/transfers/?limit=-5')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Limit must be positive'}

    response = test_client.get('/api/transfers/?order=invalid_order')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid sort order. Use "asc" or "desc"'}


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