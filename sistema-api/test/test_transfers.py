import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

from flask import Flask

from app.api import transfers  # Import your blueprint
from app.services import TransferService
from app.utils.exceptions import NotFoundException, ConflictException, InsufficientStockException, DatabaseException

# --- Fixtures ---
@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(transfers.transfers_bp)
    with app.test_client() as client:
        yield client

# --- Helper Function Tests ---
def test_validate_int_param_valid():
    assert transfers.validate_int_param("123", "test_param") == 123

def test_validate_int_param_invalid():
    with pytest.raises(ValueError, match="Invalid test_param"):
        transfers.validate_int_param("abc", "test_param")
    with pytest.raises(ValueError, match="Invalid test_param"):
        transfers.validate_int_param(None, "test_param")

def test_validate_date_param_valid():
    assert transfers.validate_date_param("2023-10-27T10:00:00", "test_date") == datetime(2023, 10, 27, 10, 0, 0)
    assert transfers.validate_date_param("2023-10-27 10:00:00+00:00", "test_date") == datetime(2023, 10, 27, 10, 0, 0)


def test_validate_date_param_invalid():
    with pytest.raises(ValueError, match="Invalid test_date format"):
        transfers.validate_date_param("2023-10-27T", "test_date")
    with pytest.raises(ValueError, match="Invalid test_date format"):
        transfers.validate_date_param("2023/10/27", "test_date")
    with pytest.raises(ValueError, match="Invalid test_date format"):
        transfers.validate_date_param("abc", "test_date")
    with pytest.raises(ValueError, match="Invalid test_date format"):
        transfers.validate_date_param(None, "test_date")


# --- create_transfer() Tests ---
def test_create_transfer_invalid_json(test_client):
    response = test_client.post(
        '/api/transfers/',
        data="invalid",
        content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


def test_create_transfer_missing_fields(test_client):
    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'user_id': 1
    })
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing required field: quantity'}

    response = test_client.post('/api/transfers/', json={
        'quantity': 10,
        'from_location_id': 1,
        'to_location_id': 2,
        'user_id': 1
    })
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Missing required field: product_id'}



def test_create_transfer_invalid_quantity(test_client):
    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': "abc",
        'user_id': 1
    })
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be a valid number'}

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': None,
        'user_id': 1
    })
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Quantity must be a valid number'}



@patch('app.api.transfers.transfer_service.get_product_by_id')
@patch('app.api.transfers.transfer_service.get_location_by_id')
@patch('app.api.transfers.transfer_service.get_user_by_id')
def test_create_transfer_not_found_product(mock_get_user, mock_get_location, mock_get_product, test_client):
    mock_get_product.side_effect = NotFoundException("Product not found")
    mock_get_location.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_user.return_value = MagicMock(to_dict=lambda: {'id': 1})

    response = test_client.post('/api/transfers/', json={
        'product_id': 999,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 1
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}



@patch('app.api.transfers.transfer_service.get_product_by_id')
@patch('app.api.transfers.transfer_service.get_location_by_id')
@patch('app.api.transfers.transfer_service.get_user_by_id')
def test_create_transfer_not_found_location(mock_get_user, mock_get_location, mock_get_product, test_client):
    mock_get_product.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_location.side_effect = NotFoundException("Location not found")
    mock_get_user.return_value = MagicMock(to_dict=lambda: {'id': 1})

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 999,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 1
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 999,
        'quantity': 10,
        'user_id': 1
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}



@patch('app.api.transfers.transfer_service.get_product_by_id')
@patch('app.api.transfers.transfer_service.get_location_by_id')
@patch('app.api.transfers.transfer_service.get_user_by_id')
def test_create_transfer_not_found_user(mock_get_user, mock_get_location, mock_get_product, test_client):
    mock_get_product.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_location.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_user.side_effect = NotFoundException("User not found")

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 999
    })
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'User not found'}



@patch('app.api.transfers.transfer_service.get_product_by_id')
@patch('app.api.transfers.transfer_service.get_location_by_id')
@patch('app.api.transfers.transfer_service.get_user_by_id')
@patch('app.api.transfers.transfer_service.get_available_stock')
def test_create_transfer_insufficient_stock(mock_get_stock, mock_get_user, mock_get_location, mock_get_product, test_client):
    mock_get_product.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_location.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_user.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_stock.return_value = 5  # Less than the transfer quantity

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 1
    })
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Insufficient stock in the source location.'}



@patch('app.api.transfers.transfer_service.get_product_by_id')
@patch('app.api.transfers.transfer_service.get_location_by_id')
@patch('app.api.transfers.transfer_service.get_user_by_id')
@patch('app.api.transfers.transfer_service.get_available_stock')
@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_success(mock_create, mock_get_stock, mock_get_user, mock_get_location, mock_get_product, test_client):
    mock_get_product.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_location.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_user.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_stock.return_value = 10
    mock_create.return_value = MagicMock(id=123, to_dict=lambda: {'id': 123})

    response = test_client.post('/api/transfers/', json={
        'product_id': 1,
        'from_location_id': 1,
        'to_location_id': 2,
        'quantity': 10,
        'user_id': 1,
        'notes': 'test note'
    })
    assert response.status_code == 201
    assert response.json == {
        'success': True,
        'message': 'Transfer registered successfully',
        'transfer_id': 123,
        'data': {'id': 123}
    }



@patch('app.api.transfers.transfer_service.get_product_by_id')
@patch('app.api.transfers.transfer_service.get_location_by_id')
@patch('app.api.transfers.transfer_service.get_user_by_id')
@patch('app.api.transfers.transfer_service.get_available_stock')
@patch('app.api.transfers.transfer_service.create_transfer')
def test_create_transfer_database_error(mock_create, mock_get_stock, mock_get_user, mock_get_location, mock_get_product, test_client):
    mock_get_product.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_location.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_user.return_value = MagicMock(to_dict=lambda: {'id': 1})
    mock_get_stock.return_value = 10
    mock_create.side_effect = DatabaseException("Database error")

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



@patch('app.api.transfers.transfer_service.get_product_by_id')
@patch('app.api.transfers.transfer_service.get_location_by_id')
@patch('app.api.transfers.transfer_service.get_user_by_id')
@patch('app.api.transfers.transfer_service.get_available_stock')
@patch('app.api.transfers.transfer_service.create_transfer')

# --- list_transfers() Tests ---
@patch('app.api.transfers.transfer_service.get_all_transfers')
def test_list_transfers_no_filters(mock_get_all, test_client):
    mock_get_all.return_value = []
    response = test_client.get('/api/transfers/')
    assert response.status_code == 200
    assert response.json == {'success': True, 'data': []}

@patch('app.api.transfers.transfer_service.get_all_transfers')
def test_list_transfers_with_valid_filters(mock_get_all, test_client):
    mock_get_all.return_value = [MagicMock(to_dict=lambda: {'id': 1})]
    response = test_client.get('/api/transfers/?productId=1&fromLocationId=2&toLocationId=3&userId=4&startDate=2023-10-26T10:00:00&endDate=2023-10-27T10:00:00&page=1&limit=10&sortBy=id&order=asc')
    assert response.status_code == 200
    assert len(response.json['data']) == 1

    mock_get_all.assert_called_once_with(filters={
        'product_id': 1,
        'from_location_id': 2,
        'to_location_id': 3,
        'user_id': 4,
        'start_date': datetime(2023, 10, 26, 10, 0, 0),
        'end_date': datetime(2023, 10, 27, 10, 0, 0)
    }, pagination={'page': 1, 'limit': 10}, sorting={'id': 'asc'})



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
    assert response.json == {'success': False, 'message': 'Invalid page number'}

    response = test_client.get('/api/transfers/?limit=abc')
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid limit number'}



@patch('app.api.transfers.transfer_service.get_all_transfers')
def test_list_transfers_database_error(mock_get_all, test_client):
    mock_get_all.side_effect = DatabaseException("DB error")
    response = test_client.get('/api/transfers/')
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}



# --- get_transfer() Tests ---
@patch('app.api.transfers.transfer_service.get_transfer_by_id')
def test_get_transfer_by_id_success(mock_get_transfer, test_client):
    mock_get_transfer.return_value = MagicMock(to_dict=lambda: {'id': 1, 'product_id': 1, 'from_location_id': 1, 'to_location_id': 2, 'quantity': 10, 'user_id': 1})
    response = test_client.get('/api/transfers/1')
    assert response.status_code == 200
    assert response.json == {'success': True, 'data': {'id': 1, 'product_id': 1, 'from_location_id': 1, 'to_location_id': 2, 'quantity': 10, 'user_id': 1}}



@patch('app.api.transfers.transfer_service.get_transfer_by_id')
def test_get_transfer_by_id_not_found(mock_get_transfer, test_client):
    mock_get_transfer.side_effect = NotFoundException("Transfer not found")
    response = test_client.get('/api/transfers/999')
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Transfer not found'}



@patch('app.api.transfers.transfer_service.get_transfer_by_id')
def test_get_transfer_by_id_database_error(mock_get_transfer, test_client):
    mock_get_transfer.side_effect = DatabaseException("DB error")
    response = test_client.get('/api/transfers/1')
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}