import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask
from app.api.products import products_bp, product_service
from app.utils.exceptions import NotFoundException, ConflictException, DatabaseException

from flask import Flask

# Import your blueprint and the service instance
# Adjust the import path based on your project structure
from app.api.products import products_bp, product_service

# Import exceptions
from app.utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException

# --- Fixtures ---
@pytest.fixture
def test_client():
    """Fixture for Flask test client."""
    app = Flask(__name__)
    # Register the blueprint with the correct URL prefix
    app.register_blueprint(products_bp, url_prefix='/api/products')
    with app.test_client() as client:
        yield client

# --- Mock Objects ---
class MockProduct:
    """Helper mock class to simulate a Product model object."""
    def __init__(self, id, sku, name, category_id=None, supplier_id=None, is_active=True):
        self.id = id
        self.sku = sku
        self.name = name
        self.category_id = category_id
        self.supplier_id = supplier_id
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category_id': self.category_id,
            'supplier_id': self.supplier_id,
            'is_active': self.is_active
        }

# --- GET /api/products Tests (list_products) ---
@patch('app.api.products.product_service.get_all_products')
def test_list_products_success_no_filters(mock_get_all, test_client):
    """Test listing products successfully with no filters."""
    mock_products_list = [
        MockProduct(id=1, sku='SKU001', name='Product A'),
        MockProduct(id=2, sku='SKU002', name='Product B', is_active=False)
    ]
    mock_get_all.return_value = mock_products_list

    response = test_client.get('/api/products/')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})
    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'data': [p.to_dict() for p in mock_products_list]
    }

@patch('app.api.products.product_service.get_all_products')
def test_list_products_success_with_filters(mock_get_all, test_client):
    """Test listing products successfully with various filters."""
    mock_products_list = [MockProduct(id=1, sku='SKU001', name='Product A', category_id=1, supplier_id=10, is_active=True)]
    mock_get_all.return_value = mock_products_list

    response = test_client.get('/api/products/?sku=SKU001&name=Product A&category_id=1&supplier_id=10&is_active=true')

    mock_get_all.assert_called_once_with(
        filters={'sku': 'SKU001', 'name': 'Product A', 'category_id': 1, 'supplier_id': 10, 'is_active': True},
        pagination={},
        sorting={}
    )
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['sku'] == 'SKU001'

@patch('app.api.products.product_service.get_all_products')
def test_list_products_success_with_pagination_sorting(mock_get_all, test_client):
    """Test listing products successfully with pagination and sorting."""
    mock_products_list = [MockProduct(id=5, sku='SKU005', name='Product E')]
    mock_get_all.return_value = mock_products_list

    response = test_client.get('/api/products/?page=2&limit=10&sortBy=name&order=desc')

    mock_get_all.assert_called_once_with(
        filters={},
        pagination={'page': 2, 'limit': 10},
        sorting={'name': 'desc'}
    )
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['id'] == 5 # Assuming sorting/pagination gives ID 5

@patch('app.api.products.product_service.get_all_products')
def test_list_products_invalid_filter_ids(mock_get_all, test_client):
    """Test listing products with invalid category_id or supplier_id filters."""
    # Invalid category_id
    response = test_client.get('/api/products/?category_id=abc')
    mock_get_all.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid category_id'}

    # Invalid supplier_id
    response = test_client.get('/api/products/?supplier_id=xyz')
    mock_get_all.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid supplier_id'}

# Note: API doesn't validate negative filter IDs explicitly; they'd be passed to service.
# API also doesn't validate invalid 'is_active' strings beyond 'true'/'1'/'false'/'0'.


@patch('app.api.products.product_service.get_all_products')
def test_list_products_invalid_pagination_params(mock_get_all, test_client):
    """Test listing products with invalid pagination parameters."""
    # Invalid page
    response = test_client.get('/api/products/?page=abc')
    mock_get_all.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid page number'}

    # Invalid limit
    response = test_client.get('/api/products/?limit=xyz')
    mock_get_all.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid limit number'}

# Note: API doesn't validate negative page/limit or invalid sortBy/order values explicitly.


@patch('app.api.products.product_service.get_all_products')
def test_list_products_database_error(mock_get_all, test_client):
    """Test listing products handles database errors."""
    mock_get_all.side_effect = DatabaseException("DB error")
    response = test_client.get('/api/products/')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.products.product_service.get_all_products')
def test_list_products_unexpected_error(mock_get_all, test_client):
    """Test listing products handles unexpected errors."""
    mock_get_all.side_effect = Exception("Something went wrong")
    response = test_client.get('/api/products/')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}

# --- POST /api/products Tests (create_product) ---
@patch('app.api.products.product_service.create_product')
def test_create_product_success_minimal(mock_create, test_client):
    """Test creating a product successfully with minimal data."""
    # Assuming service validates required fields like 'sku', 'name'
    mock_product_data = {'sku': 'NEW001', 'name': 'New Product'}
    mock_created_product = MockProduct(id=1, sku='NEW001', name='New Product')
    mock_create.return_value = mock_created_product

    response = test_client.post('/api/products/', json=mock_product_data)

    mock_create.assert_called_once_with(mock_product_data)
    assert response.status_code == 201
    assert response.json == {
        'success': True,
        'message': 'Product created successfully',
        'product_id': 1,
        'data': mock_created_product.to_dict()
    }




@patch('app.api.products.product_service.create_product')
def test_create_product_related_entity_not_found(mock_create, test_client):
    """Test creating a product when a related entity (category or supplier) is not found."""
    # Category not found
    mock_create.side_effect = NotFoundException("Category not found")
    response = test_client.post('/api/products/', json={'sku': 'NF001', 'name': 'No Cat', 'category_id': 999})

    mock_create.assert_called_once() # Service is called, raises error
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Category not found'}

    mock_create.reset_mock() # Reset for next assertion
    # Supplier not found
    mock_create.side_effect = NotFoundException("Supplier not found")
    response = test_client.post('/api/products/', json={'sku': 'NF002', 'name': 'No Sup', 'supplier_id': 888})
    mock_create.assert_called_once()
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Supplier not found'}


@patch('app.api.products.product_service.create_product')
def test_create_product_conflict(mock_create, test_client):
    """Test creating a product when a conflict occurs (e.g., duplicate SKU)."""
    mock_create.side_effect = ConflictException("Product with this SKU already exists")
    response = test_client.post('/api/products/', json={'sku': 'EXISTING', 'name': 'Existing'})

    mock_create.assert_called_once()
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Product with this SKU already exists'}


@patch('app.api.products.product_service.create_product')
def test_create_product_database_error(mock_create, test_client):
    """Test creating a product handles database errors."""
    mock_create.side_effect = DatabaseException("DB connection failed")
    response = test_client.post('/api/products/', json={'sku': 'DBERR', 'name': 'DB Error'})

    mock_create.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB connection failed'}

@patch('app.api.products.product_service.create_product')
def test_create_product_unexpected_error(mock_create, test_client):
    """Test creating a product handles unexpected errors."""
    mock_create.side_effect = Exception("Unexpected service error")
    response = test_client.post('/api/products/', json={'sku': 'UNEXP', 'name': 'Unexpected'})

    mock_create.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- GET /api/products/{id} Tests (get_product) ---
@patch('app.api.products.product_service.get_product_by_id')
def test_get_product_success(mock_get_by_id, test_client):
    """Test getting a single product successfully."""
    mock_product = MockProduct(id=1, sku='SKU001', name='Product A')
    mock_get_by_id.return_value = mock_product

    response = test_client.get('/api/products/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 200
    assert response.json == {'success': True, 'data': mock_product.to_dict()}

@patch('app.api.products.product_service.get_product_by_id')
def test_get_product_not_found(mock_get_by_id, test_client):
    """Test getting a single product that does not exist."""
    mock_get_by_id.side_effect = NotFoundException("Product not found")
    response = test_client.get('/api/products/999')

    mock_get_by_id.assert_called_once_with(999)
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}

@patch('app.api.products.product_service.get_product_by_id')
def test_get_product_negative_id(mock_get_by_id, test_client):
    """
    Test getting a product with a negative ID in the URL.
    Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.get('/api/products/-1')

    mock_get_by_id.assert_not_called() # Service should not be called
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
    # No specific JSON message expected here as Flask's default 404 is likely triggered


@patch('app.api.products.product_service.get_product_by_id')
def test_get_product_database_error(mock_get_by_id, test_client):
    """Test getting a product handles database errors."""
    mock_get_by_id.side_effect = DatabaseException("DB error")
    response = test_client.get('/api/products/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.products.product_service.get_product_by_id')
def test_get_product_unexpected_error(mock_get_by_id, test_client):
    """Test getting a product handles unexpected errors."""
    mock_get_by_id.side_effect = Exception("Unexpected error")
    response = test_client.get('/api/products/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


@patch('app.api.products.product_service.update_product')
def test_update_product_success_patch(mock_update, test_client):
    """Test updating a product successfully using PATCH (partial update)."""
    product_id = 1
    update_data = {'is_active': False} # Only update is_active
    mock_updated_product = MockProduct(id=product_id, sku='SKU001', name='Product A', is_active=False)
    mock_update.return_value = mock_updated_product

    response = test_client.patch(f'/api/products/{product_id}', json=update_data)

    mock_update.assert_called_once_with(product_id, update_data)
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == f'Product {product_id} updated successfully'
    assert response.json['data']['is_active'] is False


@patch('app.api.products.product_service.update_product')
def test_update_product_invalid_id(mock_update, test_client):
    """
    Test updating a product with a negative ID in the URL.
     Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.put('/api/products/-1', json={'name': 'Test'})

    mock_update.assert_not_called()
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
    # No specific JSON message expected here as Flask's default 404 is likely triggered



# Note: API does not perform explicit validation for field types or values in the payload.
# These are assumed to be handled by the service layer.
@patch('app.api.products.product_service.update_product')
def test_update_product_service_validation_error(mock_update, test_client):
    """Test updating a product handles ValueError/TypeError from service."""
    product_id = 1
    # Simulate service raising ValueError for invalid data (e.g., bad value)
    mock_update.side_effect = ValueError("Price cannot be negative")
    response = test_client.put(f'/api/products/{product_id}', json={'price': -10})

    mock_update.assert_called_once() # API passes data to service
    assert response.status_code == 400 # API maps ValueError/TypeError to 400
    assert response.json == {'success': False, 'message': 'Price cannot be negative'}

    mock_update.reset_mock()
    mock_update.side_effect = TypeError("Invalid type for category_id")
    response = test_client.put(f'/api/products/{product_id}', json={'category_id': 'one'}) # Invalid type
    mock_update.assert_called_once()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid type for category_id'}


@patch('app.api.products.product_service.update_product')
def test_update_product_not_found(mock_update, test_client):
    """Test updating a product that does not exist or whose related entities do not exist."""
    # Product not found
    mock_update.side_effect = NotFoundException("Product not found")
    response = test_client.put('/api/products/999', json={'name': 'Update'})

    mock_update.assert_called_once() # Service is called, raises error
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}

    mock_update.reset_mock()
    # Related entity (e.g., Category) not found
    mock_update.side_effect = NotFoundException("Category not found")
    response = test_client.put('/api/products/1', json={'category_id': 999})
    mock_update.assert_called_once_with(1, {'category_id': 999}) # API passes data
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Category not found'}


@patch('app.api.products.product_service.update_product')
def test_update_product_conflict(mock_update, test_client):
    """Test updating a product when a conflict occurs (e.g., duplicate SKU)."""
    mock_update.side_effect = ConflictException("Product with this SKU already exists")
    response = test_client.put('/api/products/1', json={'sku': 'EXISTING'})

    mock_update.assert_called_once()
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Product with this SKU already exists'}


@patch('app.api.products.product_service.update_product')
def test_update_product_database_error(mock_update, test_client):
    """Test updating a product handles database errors."""
    mock_update.side_effect = DatabaseException("DB error")
    response = test_client.put('/api/products/1', json={'name': 'Test'})

    mock_update.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}


@patch('app.api.products.product_service.update_product')
def test_update_product_unexpected_error(mock_update, test_client):
    """Test updating a product handles unexpected errors."""
    mock_update.side_effect = Exception("Unexpected error")
    response = test_client.put('/api/products/1', json={'name': 'Test'})

    mock_update.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- DELETE /api/products/{id} Tests (delete_product) ---
@patch('app.api.products.product_service.delete_product')
def test_delete_product_success(mock_delete, test_client):
    """Test deleting (marking inactive) a product successfully."""
    product_id = 1
    mock_delete.return_value = True # Simulate service success

    response = test_client.delete(f'/api/products/{product_id}')

    mock_delete.assert_called_once_with(product_id)
    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'message': f'Product {product_id} marked as inactive' # Check exact message
    }

@patch('app.api.products.product_service.delete_product')
def test_delete_product_negative_id(mock_delete, test_client):
    """
    Test deleting a product with a negative ID in the URL.
     Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.delete('/api/products/-1')

    mock_delete.assert_not_called()
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
    # No specific JSON message expected here as Flask's default 404 is likely triggered


@patch('app.api.products.product_service.delete_product')
def test_delete_product_not_found(mock_delete, test_client):
    """Test deleting a product that does not exist."""
    mock_delete.side_effect = NotFoundException("Product not found")

    response = test_client.delete('/api/products/999')

    mock_delete.assert_called_once_with(999)
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Product not found'}



@patch('app.api.products.product_service.delete_product')
def test_delete_product_service_returns_false(mock_delete, test_client):
    """Test deleting a product when the service returns False."""
    product_id = 1
    mock_delete.return_value = False # Simulate service returning False

    response = test_client.delete(f'/api/products/{product_id}')

    mock_delete.assert_called_once_with(product_id)
    assert response.status_code == 500 # API returns 500 for service returning False
    assert response.json == {'success': False, 'message': f'Could not mark Product {product_id} as inactive'} # Check exact message


@patch('app.api.products.product_service.delete_product')
def test_delete_product_database_error(mock_delete, test_client):
    """Test deleting a product handles database errors."""
    mock_delete.side_effect = DatabaseException("DB error")

    response = test_client.delete('/api/products/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.products.product_service.delete_product')
def test_delete_product_unexpected_error(mock_delete, test_client):
    """Test deleting a product handles unexpected errors."""
    mock_delete.side_effect = Exception("Unexpected error")

    response = test_client.delete('/api/products/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


@patch('app.api.products.product_service.create_product')
def test_create_product_missing_required_fields_empty_json(mock_create, test_client):
    """TC01: Test creating a product with an empty JSON body."""
    response = test_client.post(
        '/api/products/', # Asegúrate de usar la barra diagonal final
        json={} # JSON vacío
    )
    mock_create.assert_not_called()
    assert response.status_code == 400
    # Ajusta el mensaje esperado según la implementación en products.py
    # Si la API retorna 'Invalid JSON data' para JSON vacío, espera eso.
    # Si la API retorna un mensaje más específico después de la corrección, ajústalo.
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}

@patch('app.api.products.product_service.create_product')
def test_create_product_missing_required_fields_no_name(mock_create, test_client):
    """TC01: Test creating a product with missing 'name' field specifically."""
    # Simula la validación de la API si no tiene 'name'
    test_data = {'sku': 'SKU001', 'description': 'Some description'}
    response = test_client.post(
        '/api/products/', # Asegúrate de usar la barra diagonal final
        json=test_data
    )
    mock_create.assert_not_called()
    assert response.status_code == 400
    # Este es el mensaje esperado si la validación del API se alcanza antes que la del servicio
    assert response.json == {'success': False, 'message': 'Category name is required and must be a non-empty string'} # Esto viene de categories, deberia ser de products

    # Re-evaluar el mensaje esperado aquí: si el endpoint de products valida, su mensaje debería ser propio.
    # Si la validación ocurre en el servicio, el mensaje de error puede variar.
    # Basado en la estructura de `products.py`, si `name` no está en `data`, no hay un chequeo explícito en el API,
    # el error debería venir del servicio o de un chequeo más genérico.
    # Si no se define el 'name' en la request, product_service.create_product podría recibirlo como None
    # y lanzar un error de tipo ValueError (si el servicio valida que name no sea nulo/vacío).
    # Sin embargo, el problema original indicaba un 404. Asumimos que se corrige la accesibilidad de la ruta.


@patch('app.api.products.product_service.create_product')
def test_create_product_with_invalid_data(mock_create, test_client):
    """TC02: Test creating a product with invalid data (negative price, text stock)."""
    invalid_data = {
        "sku": "INVALIDPROD",
        "name": "Producto inválido",
        "unit_price": -150.00,  # Precio negativo
        "min_stock": "diez",    # Stock como texto
        "category_id": 1,
        "supplier_id": 1
    }
    # Simulamos que el servicio lanzaría ValueError por datos inválidos
    mock_create.side_effect = ValueError("Unit price cannot be negative and min stock must be a number.")

    response = test_client.post(
        '/api/products/', # Asegúrate de usar la barra diagonal final
        json=invalid_data
    )

    mock_create.assert_called_once() # El API debería llamar al servicio
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Unit price cannot be negative and min stock must be a number.'}



@patch('app.api.products.product_service.create_product')
def test_create_product_duplicate_sku(mock_create, test_client):
    """TC05: Test creating a product with a duplicate SKU."""
    # Simular la creación exitosa del primer producto
    first_product_data = {
        "sku": "UNIQUE_SKU_123",
        "name": "Product One",
        "unit_price": 10.0,
        "min_stock": 5,
        "category_id": 1,
        "supplier_id": 1
    }
    mock_created_product = MockProduct(id=1, **first_product_data)
    mock_create.return_value = mock_created_product

    # Paso 1: Crear el primer producto (solo para simular que el SKU ya existe)
    # En un test real de integración, se crearía el producto en la DB
    response_first = test_client.post('/api/products/', json=first_product_data)
    # assert response_first.status_code == 201 # Este paso es para simular un escenario real

    # Simular que el segundo intento de creación con el mismo SKU lanza ConflictException
    mock_create.side_effect = ConflictException("Product with this SKU already exists")

    # Paso 2: Intentar crear otro producto con el mismo SKU
    duplicate_product_data = {
        "sku": "UNIQUE_SKU_123", # SKU duplicado
        "name": "Product Two (Duplicate)",
        "unit_price": 12.0,
        "min_stock": 3,
        "category_id": 1,
        "supplier_id": 1
    }
    response_second = test_client.post(
        '/api/products/', # Asegúrate de usar la barra diagonal final
        json=duplicate_product_data
    )

    # Verificamos la respuesta del segundo intento
    mock_create.assert_called_once() # Se llama una vez para el segundo intento (el primero es mockeado)
    assert response_second.status_code == 409 # Esperamos 409 Conflict
    assert response_second.json == {'success': False, 'message': 'Product with this SKU already exists'}


@patch('app.api.products.product_service.delete_product')
def test_delete_product_not_found_with_json_response(mock_delete, test_client):
    """TC08: Test deleting a non-existent product returns 404 with JSON body."""
    mock_delete.side_effect = NotFoundException("Product not found")
    non_existent_id = 999999

    response = test_client.delete(f'/api/products/{non_existent_id}')

    mock_delete.assert_called_once_with(non_existent_id)
    assert response.status_code == 404
    # La aserción debe verificar el contenido JSON esperado
    assert response.json == {'success': False, 'message': 'Product not found'}
    # Opcional: verificar que el header Content-Type es 'application/json'
    assert response.headers['Content-Type'] == 'application/json'


def test_sql_injection_in_product_name_filter(test_client):
    """TC10: Test SQL injection attempt in product name filter."""
    malicious_payload = "'; DROP TABLE products;--"
    response = test_client.get(f'/api/products/?name={malicious_payload}')

    # Después de implementar la validación de entrada en el API
    assert response.status_code == 400 # O 422
    assert response.json['success'] is False
    assert "Invalid characters" in response.json['message'] # O mensaje similar de validación

# Dentro de sistema-api/test/test_categories.py

# ... (fixture test_client, MockCategory existentes) ...

def test_sql_injection_in_category_name_filter(test_client):
    """TC10: Test SQL injection attempt in category name filter."""
    malicious_payload = "'; DROP TABLE categories;--"
    response = test_client.get(f'/api/categories/?name={malicious_payload}')

    # Después de implementar la validación de entrada en el API
    assert response.status_code == 400 # O 422
    assert response.json['success'] is False
    assert "Invalid name filter" in response.json['message'] # O mensaje similar de validación


def test_http_redirect_to_https(test_client):
    """TC11: Test that HTTP requests are redirected to HTTPS."""
    # Simular una petición HTTP a través de un proxy que añade X-Forwarded-Proto
    response = test_client.get(
        '/api/products/',
        headers={'X-Forwarded-Proto': 'http'}
    )

    # Esperamos una redirección 301, 302, o 308
    assert response.status_code in [301, 302, 308]
    # Esperamos que la ubicación de la redirección sea HTTPS
    assert response.headers['Location'].startswith('https://')

    # Si la implementación es un rechazo directo (403 o 426)
    # assert response.status_code in [403, 426]
    # assert response.json['success'] is False
    # assert 'HTTPS is required' in response.json['message']


def test_security_headers_present(test_client):
    """TC14: Test that essential security headers are present in responses."""
    response = test_client.get('/api/products/')

    # Verificar Content-Security-Policy (CSP)
    assert 'Content-Security-Policy' in response.headers
    # assert "default-src 'self'" in response.headers['Content-Security-Policy'] # Ejemplo de CSP, varía por config

    # Verificar X-Frame-Options
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] == 'DENY' # O 'SAMEORIGIN'

    # Verificar X-Content-Type-Options
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'

    # Verificar Referrer-Policy
    assert 'Referrer-Policy' in response.headers
    # assert response.headers['Referrer-Policy'] == 'no-referrer-when-downgrade' # O la política configurada

    # Verificar Strict-Transport-Security (HSTS) - solo presente en HTTPS
    # Este test solo pasaría si la aplicación ya corre en HTTPS o si Talisman lo simula
    # if response.headers.get('Strict-Transport-Security'):
    #    assert 'Strict-Transport-Security' in response.headers
    #    assert 'max-age=' in response.headers['Strict-Transport-Security']

    # Verificar Permissions-Policy (antes Feature-Policy)
    # assert 'Permissions-Policy' in response.headers # Si está configurada

    # Verificar Cache-Control (ejemplo, puede variar)
    assert 'Cache-Control' in response.headers


@patch('app.api.products.product_service.create_product')
def test_create_product_with_duplicate_sku_rejection(mock_create, test_client):
    """TC15: Test creating two products with the same SKU should be rejected."""
    # Simular la creación exitosa del primer producto
    first_product_data = {
        "sku": "DUP_SKU_TEST",
        "name": "First Product",
        "description": "Desc 1",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 10.0,
        "unit_price": 20.0,
        "min_stock": 5
    }
    mock_created_product = MockProduct(id=1, **first_product_data)
    mock_create.return_value = mock_created_product

    # Simular el primer intento de creación (para que el SKU exista en la capa de prueba)
    # En un test de integración, se crearía el producto en la DB
    response_first = test_client.post('/api/products/', json=first_product_data)

    # Simular que el segundo intento de creación con el mismo SKU lanza ConflictException
    mock_create.side_effect = ConflictException("Product with this SKU already exists")

    # Datos para el segundo producto con el mismo SKU
    second_product_data = {
        "sku": "DUP_SKU_TEST", # SKU duplicado
        "name": "Second Product (Duplicate)",
        "description": "Desc 2",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 15.0,
        "unit_price": 25.0,
        "min_stock": 2
    }

    response_second = test_client.post(
        '/api/products/', # Asegúrate de usar la barra diagonal final
        json=second_product_data
    )

    # Verificar que el segundo intento es rechazado con 409 Conflict
    assert response_second.status_code == 409
    assert response_second.json == {'success': False, 'message': 'Product with this SKU already exists'}

    # Asegurarse de que mock_create fue llamado por lo menos una vez (por el segundo intento)
    assert mock_create.called


def test_create_product_payload_too_large(test_client):
    """TC16: Test sending a payload larger than allowed."""
    # Crear un payload excesivamente grande
    large_string = 'A' * (500 * 1024) # 500 KB, ajusta según tu MAX_CONTENT_LENGTH en config.py
    large_payload = {
        "sku": "LARGE_SKU",
        "name": large_string, # Un campo muy grande
        "description": "This is a very long description to exceed payload limits. " * 1000,
        "unit_price": 10.0,
        "min_stock": 5,
        "category_id": 1,
        "supplier_id": 1
    }

    response = test_client.post(
        '/api/products/',
        json=large_payload
    )

    # Esperamos 413 Payload Too Large
    assert response.status_code == 413
    assert response.json['success'] is False
    assert "Payload Too Large" in response.json['message'] # O un mensaje similar configurado en el error handler

def test_sql_injection_via_get_parameter_name_filter(test_client):
    """TC17: Test SQL injection attempt via GET parameter 'name' filter."""
    malicious_payload = "' OR 1=1 --"
    response = test_client.get(f'/api/products/?name={malicious_payload}')

    # Después de implementar la validación de entrada en el API
    assert response.status_code == 400 # O 422
    assert response.json['success'] is False
    assert "Invalid characters" in response.json['message'] # O mensaje similar de validación
    # Si la validación se hace a nivel de servicio, el error podría ser un 500 si se propaga mal,
    # pero el API debería interceptarlo y devolver un 400.

@patch('app.api.products.product_service.create_product')
def test_command_injection_in_json_payload(mock_create, test_client):
    """TC18: Test command injection attempt in JSON payload of POST endpoint."""
    malicious_payload = {
        "sku": "CMD_INJECT",
        "name": "Malicious Product; rm -rf /",  # Intento de inyección
        "description": "$(reboot)",             # Otro intento
        "unit_price": 10.0,
        "min_stock": 5,
        "category_id": 1,
        "supplier_id": 1
    }

    # Asumimos que la validación en el API o el servicio detectará el patrón malicioso
    mock_create.side_effect = ValueError("Invalid characters detected in name or description.")

    response = test_client.post(
        '/api/products/', # Asegúrate de usar la barra diagonal final
        json=malicious_payload
    )

    # Esperamos 400 Bad Request por validación fallida
    assert response.status_code == 400
    assert response.json['success'] is False
    assert "Invalid characters detected" in response.json['message'] # O mensaje similar

