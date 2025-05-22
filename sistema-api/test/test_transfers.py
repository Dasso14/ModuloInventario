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
def test_transfer_exceeds_available_stock(client):
    # Paso 1: Crear un producto (asegúrate que este endpoint funcione)
    # Para este test, podrías mockear la existencia del producto y su stock directamente
    # si la creación de producto es el problema.
    # Aquí se asume que puedes crear un producto y que el servicio de inventario
    # puede verificar su stock.

    # Crear ubicaciones si el servicio las necesita
    loc1_resp = client.post('/api/locations/', json={"name": "Almacen Origen TC03"})
    assert loc1_resp.status_code in (200, 201, 409) # 409 si ya existe
    loc1_id = loc1_resp.get_json().get("location_id") if loc1_resp.status_code != 409 else client.get('/api/locations/?name=Almacen Origen TC03').get_json()['data'][0]['id']


    loc2_resp = client.post('/api/locations/', json={"name": "Almacen Destino TC03"})
    assert loc2_resp.status_code in (200, 201, 409)
    loc2_id = loc2_resp.get_json().get("location_id") if loc2_resp.status_code != 409 else client.get('/api/locations/?name=Almacen Destino TC03').get_json()['data'][0]['id']

    # Crear producto
    product_payload = {
        "sku": "TC03_PROD",
        "name": "Producto Test TC03",
        "category_id": 1, # Asume que existe
        "supplier_id": 1, # Asume que existe
        "unit_cost": 10.0,
        "unit_price": 20.0
    }
    product_resp = client.post('/api/products/', json=product_payload)
    assert product_resp.status_code in (200, 201), f"Falló la creación de producto: {product_resp.get_data(as_text=True)}"
    product_id = product_resp.get_json()["data"]["id"]

    # Añadir stock inicial al producto en la ubicación de origen
    add_stock_payload = {
        "product_id": product_id,
        "location_id": loc1_id,
        "quantity": 5, # Stock disponible = 5
        "user_id": 1 # Asume que existe
    }
    add_stock_resp = client.post('/api/inventory/add', json=add_stock_payload)
    assert add_stock_resp.status_code == 201, f"Falló al añadir stock: {add_stock_resp.get_data(as_text=True)}"

    # Paso 2: Intentar hacer transferencia con cantidad mayor al stock
    transfer_payload = {
        "product_id": product_id,
        "from_location_id": loc1_id,
        "to_location_id": loc2_id,
        "quantity": 10,  # Cantidad mayor que el stock disponible (5)
        "user_id": 1 # Asume que existe
    }
    transfer_resp = client.post('/api/inventory/transfer', json=transfer_payload) # Endpoint de inventory para transferir

    assert transfer_resp.status_code == 409, "Debe rechazar transferencia con cantidad mayor al stock (409 Conflict)"
    data = transfer_resp.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "insufficient stock" in data.get("message", "").lower() or "insuficiente" in data.get("message", "").lower()
# Archivo: sistema-api/test/test_transfers.py (o test_inventory.py)

def test_no_negative_stock_after_transfer_movement(client):
    # Crear ubicaciones
    loc_A_resp = client.post('/api/locations/', json={"name": "Almacen Origen TC06"})
    assert loc_A_resp.status_code in (201, 409)
    loc_A_id = loc_A_resp.get_json().get("location_id") if loc_A_resp.status_code != 409 else client.get('/api/locations/?name=Almacen Origen TC06').get_json()['data'][0]['id']

    loc_B_resp = client.post('/api/locations/', json={"name": "Almacen Destino TC06"})
    assert loc_B_resp.status_code in (201, 409)
    loc_B_id = loc_B_resp.get_json().get("location_id") if loc_B_resp.status_code != 409 else client.get('/api/locations/?name=Almacen Destino TC06').get_json()['data'][0]['id']

    # Crear producto
    product_payload = {
        "sku": "TC06_PROD_NEG_STOCK",
        "name": "Producto Stock Negativo TC06",
        "category_id": 1, # Asume que existe
        "supplier_id": 1, # Asume que existe
        "unit_cost": 50.0,
        "unit_price": 100.0
    }
    product_resp = client.post('/api/products/', json=product_payload)
    assert product_resp.status_code in (200, 201), f"Falló la creación de producto: {product_resp.get_data(as_text=True)}"
    product_id = product_resp.get_json()["data"]["id"]

    # Añadir stock inicial
    add_stock_payload = {
        "product_id": product_id,
        "location_id": loc_A_id,
        "quantity": 5, # Stock disponible = 5
        "user_id": 1 # Asume que existe
    }
    add_stock_resp = client.post('/api/inventory/add', json=add_stock_payload)
    assert add_stock_resp.status_code == 201, f"Falló al añadir stock: {add_stock_resp.get_data(as_text=True)}"

    # Intentar transferencia que dejaría stock negativo (o es mayor al disponible)
    transfer_payload = {
        "product_id": product_id,
        "from_location_id": loc_A_id,
        "to_location_id": loc_B_id,
        "quantity": 10, # Mayor que el stock disponible (5)
        "user_id": 1
    }
    # El endpoint para transferencias es /api/inventory/transfer según tu inventory.py
    transfer_resp = client.post('/api/inventory/transfer', json=transfer_payload)

    # El InventoryService.create_location_transfer debería lanzar InsufficientStockException,
    # y el endpoint /api/inventory/transfer lo mapea a 409.
    assert transfer_resp.status_code == 409, "Debe rechazar movimiento que deja stock negativo o excede el disponible (409 Conflict)"
    data = transfer_resp.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "insufficient stock" in data.get("message", "").lower() or "insuficiente" in data.get("message", "").lower()
# Archivo: sistema-api/test/test_transfers.py (o test_inventory.py)

def test_transfer_exceeds_available_stock_again(client): # Nombre ligeramente modificado para evitar duplicados exactos de función
    # Paso 1: Crear producto con stock limitado y ubicaciones
    loc_C_resp = client.post('/api/locations/', json={"name": "Almacen Origen TC07"})
    assert loc_C_resp.status_code in (201, 409)
    loc_C_id = loc_C_resp.get_json().get("location_id") if loc_C_resp.status_code != 409 else client.get('/api/locations/?name=Almacen Origen TC07').get_json()['data'][0]['id']

    loc_D_resp = client.post('/api/locations/', json={"name": "Almacen Destino TC07"})
    assert loc_D_resp.status_code in (201, 409)
    loc_D_id = loc_D_resp.get_json().get("location_id") if loc_D_resp.status_code != 409 else client.get('/api/locations/?name=Almacen Destino TC07').get_json()['data'][0]['id']

    product_payload = {
        "sku": "TC07_PROD_STOCK",
        "name": "Producto Test Stock TC07",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 100.0,
        "unit_price": 150.0
    }
    product_resp = client.post('/api/products/', json=product_payload)
    assert product_resp.status_code in (200, 201), f"Falló la creación de producto: {product_resp.get_data(as_text=True)}"
    product_id = product_resp.get_json()["data"]["id"]

    # Añadir stock
    add_stock_payload = {
        "product_id": product_id,
        "location_id": loc_C_id,
        "quantity": 5,  # Stock disponible = 5
        "user_id": 1
    }
    add_stock_resp = client.post('/api/inventory/add', json=add_stock_payload)
    assert add_stock_resp.status_code == 201, f"Falló al añadir stock: {add_stock_resp.get_data(as_text=True)}"

    # Paso 2: Intentar hacer transferencia con cantidad mayor al stock
    transfer_payload = {
        "product_id": product_id,
        "from_location_id": loc_C_id,
        "to_location_id": loc_D_id,
        "quantity": 10,  # mayor que stock disponible
        "user_id": 1
    }
    transfer_resp = client.post('/api/inventory/transfer', json=transfer_payload) # Endpoint de inventory

    assert transfer_resp.status_code == 409, "Debe rechazar transferencia por stock insuficiente (409 Conflict)"
    data = transfer_resp.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "insufficient stock" in data.get("message", "").lower() or "insuficiente" in data.get("message", "").lower()
def test_create_transfer_with_same_origin_and_destination(client):
    # Crear producto y ubicación
    loc_G_resp = client.post('/api/locations/', json={"name": "Almacen G TC19"})
    assert loc_G_resp.status_code in (201, 409)
    loc_G_id = loc_G_resp.get_json().get("location_id") if loc_G_resp.status_code != 409 else client.get('/api/locations/?name=Almacen G TC19').get_json()['data'][0]['id']

    product_payload = {
        "sku": "TC19_PROD_SAME_LOC",
        "name": "Producto Misma Loc TC19",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 10.0,
        "unit_price": 20.0
    }
    product_resp = client.post('/api/products/', json=product_payload)
    assert product_resp.status_code in (200, 201), f"Falló la creación de producto: {product_resp.get_data(as_text=True)}"
    product_id = product_resp.get_json()["data"]["id"]

    # Añadir stock para que no falle por insuficiencia
    add_stock_payload = {
        "product_id": product_id,
        "location_id": loc_G_id,
        "quantity": 10,
        "user_id": 1
    }
    add_stock_resp = client.post('/api/inventory/add', json=add_stock_payload)
    assert add_stock_resp.status_code == 201

    # Intentar transferencia con mismo origen y destino
    transfer_payload = {
        "product_id": product_id,
        "from_location_id": loc_G_id,
        "to_location_id": loc_G_id, # Mismo ID
        "quantity": 5,
        "user_id": 1
    }
    transfer_resp = client.post('/api/inventory/transfer', json=transfer_payload) # Endpoint de inventory

    # Tu `inventory.py` en `transfer_stock` tiene:
    # if data['from_location_id'] == data['to_location_id']:
    #    return jsonify({'success': False, 'message': 'Source and destination locations cannot be the same'}), 400
    assert transfer_resp.status_code == 400, "Debe rechazar transferencia con mismo origen y destino"
    data = transfer_resp.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "same" in data.get("message", "").lower() or "no pueden ser la misma" in data.get("message", "").lower()
def test_delete_nonexistent_transfer(client):
    nonexistent_transfer_id = 999999
    # Asumiendo que el endpoint es DELETE /api/transfers/{id} (sin / al final)
    # y que el servicio TransferService.delete_transfer(id) existe y es llamado.
    response = client.delete(f'/api/transfers/{nonexistent_transfer_id}') # Sin / al final

    # Si el endpoint NO EXISTE, el código será 404 (o 405 si la ruta base existe pero no para DELETE).
    # Si EXISTE y el servicio lanza NotFoundException:
    #   tu BaseService._delete, si es usado, relanzaría NotFoundException.
    #   El manejador de excepciones en el endpoint debería convertirlo a un JSON 404.

    # Ejemplo de cómo se vería en transfers.py:
    # @transfers_bp.route('/<int:transfer_id>', methods=['DELETE'])
    # def delete_transfer_route(transfer_id):
    #     try:
    #         transfer_service.delete_transfer(transfer_id) # Asumiendo que existe
    #         return jsonify({'success': True, 'message': 'Transfer deleted'}), 200
    #     except NotFoundException as e:
    #         return jsonify({'success': False, 'message': str(e)}), 404
    #     # ... otros manejadores de excepción ...

    assert response.status_code == 404, "Debe devolver 404 Not Found al eliminar transferencia inexistente"
    data = response.get_json()
    
    # Esta aserción fallará si el endpoint no existe y devuelve HTML 404, o si no devuelve JSON.
    assert data is not None, "La respuesta debe contener un cuerpo JSON con el error"
    assert data.get("success") is False
    assert "not found" in data.get("message", "").lower() or "no existe" in data.get("message", "").lower()
def test_update_nonexistent_transfer(client):
    nonexistent_transfer_id = 999999
    update_payload = {
        "notes": "Intentando actualizar una transferencia fantasma"
        # Incluir otros campos que el endpoint de actualización esperaría
    }
    # Asumiendo que el endpoint es PUT /api/transfers/{id} (sin / al final)
    response = client.put(f'/api/transfers/{nonexistent_transfer_id}', json=update_payload) # Sin / al final

    # Comportamiento similar al delete: si no existe el endpoint -> 404/405.
    # Si existe y el servicio lanza NotFoundException:
    assert response.status_code == 404, "Debe devolver 404 Not Found al actualizar transferencia inexistente"
    data = response.get_json()
    assert data is not None, "La respuesta debe contener un cuerpo JSON con el error"
    assert data.get("success") is False
    assert "not found" in data.get("message", "").lower() or "no existe" in data.get("message", "").lower()
def test_create_transfer_with_negative_quantity(client):
    # Crear producto y ubicaciones
    loc_H_resp = client.post('/api/locations/', json={"name": "Almacen H TC22"})
    assert loc_H_resp.status_code in (201, 409)
    loc_H_id = loc_H_resp.get_json().get("location_id") if loc_H_resp.status_code != 409 else client.get('/api/locations/?name=Almacen H TC22').get_json()['data'][0]['id']

    loc_I_resp = client.post('/api/locations/', json={"name": "Almacen I TC22"})
    assert loc_I_resp.status_code in (201, 409)
    loc_I_id = loc_I_resp.get_json().get("location_id") if loc_I_resp.status_code != 409 else client.get('/api/locations/?name=Almacen I TC22').get_json()['data'][0]['id']

    product_payload = {
        "sku": "TC22_PROD_NEG_QTY",
        "name": "Producto Cant Negativa TC22",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 10.0,
        "unit_price": 20.0
    }
    product_resp = client.post('/api/products/', json=product_payload)
    assert product_resp.status_code in (200, 201), f"Falló la creación de producto: {product_resp.get_data(as_text=True)}"
    product_id = product_resp.get_json()["data"]["id"]

    # Añadir stock para que la validación de stock suficiente no sea el problema
    add_stock_payload = {
        "product_id": product_id,
        "location_id": loc_H_id,
        "quantity": 100, # Stock amplio
        "user_id": 1
    }
    add_stock_resp = client.post('/api/inventory/add', json=add_stock_payload)
    assert add_stock_resp.status_code == 201

    # Intentar transferencia con cantidad negativa
    transfer_payload = {
        "product_id": product_id,
        "from_location_id": loc_H_id,
        "to_location_id": loc_I_id,
        "quantity": -5, # Cantidad negativa
        "user_id": 1
    }
    transfer_resp = client.post('/api/inventory/transfer', json=transfer_payload) # Endpoint de inventory

    # Tu `inventory.py` en `transfer_stock` tiene:
    # if quantity <= 0:
    #    return jsonify({'success': False, 'message': 'Quantity must be positive for transfer'}), 400
    assert transfer_resp.status_code == 400, "Debe rechazar transferencia con cantidad negativa"
    data = transfer_resp.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "quantity must be positive" in data.get("message", "").lower() or "cantidad debe ser positiva" in data.get("message", "").lower()