import pytest
import json
from unittest.mock import MagicMock, patch

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
def test_create_product_without_required_fields(client):
    payload = {}  # Sin campos
    response = client.post('/api/products', json=payload) # Nota: el test usa /api/products sin /

    assert response.status_code == 400, "Esperamos 400 Bad Request al no enviar campos requeridos"
    data = response.get_json()
    assert "message" in data or "error" in data, "Debe haber un mensaje de error explicativo"
def test_create_product_with_invalid_data(client):
    payload = {
        "name": "Producto inválido TC02", # Added name for completeness
        "sku": "INVTC02", # Added SKU for completeness
        "price": -150.00,    # Precio inválido (negativo)
        "stock": "diez",     # Stock inválido (texto en vez de número)
        "category_id": 1     # Assuming category 1 exists
    }
    response = client.post('/api/products/', json=payload)

    assert response.status_code == 400, "Esperamos 400 Bad Request por datos inválidos"
    data = response.get_json()
    assert "message" in data, "Debe existir un mensaje de error explicativo"
    # This assertion might need to be more specific based on actual error messages
    assert ("price" in data["message"].lower() or "stock" in data["message"].lower() or "invalid number" in data["message"].lower() or "valid integer" in data["message"].lower()), \
           "Mensaje debe mencionar los campos inválidos o la naturaleza del error"
# Archivo: sistema-api/test/test_products.py

def test_create_product_with_duplicate_sku(client): # Renombrado para reflejar lo que se prueba (SKU)
    # Asumiendo que la categoría y proveedor existen
    client.post('/api/categories/', json={"name": "Categoria Test TC05", "description": "Desc"}) # Crear si no existe
    client.post('/api/suppliers/', json={"name": "Proveedor Test TC05"}) # Crear si no existe

    sku_val = "SKU_DUPLICADO_TC05"
    product_payload_1 = {
        "sku": sku_val,
        "name": "Producto Original TC05",
        "category_id": 1, # Asume que existe o usa el ID de la categoría creada arriba
        "supplier_id": 1, # Asume que existe o usa el ID del proveedor creado arriba
        "unit_cost": 50.0,
        "unit_price": 100.0,
        # "min_stock": 10 # No es requerido en el modelo base, pero sí en tu ProductService
    }
    resp1 = client.post('/api/products/', json=product_payload_1) # URL con /
    assert resp1.status_code in (200, 201), f"Falló la creación del primer producto: {resp1.get_data(as_text=True)}"
    assert resp1.get_json()["success"] is True

    product_payload_2 = {
        "sku": sku_val, # Mismo SKU
        "name": "Producto Duplicado TC05",
        "category_id": 1,
        "supplier_id": 1,
        "unit_cost": 60.0,
        "unit_price": 120.0
    }
    resp2 = client.post('/api/products/', json=product_payload_2) # URL con /

    assert resp2.status_code == 409, "Debe rechazar producto con SKU duplicado (409 Conflict)"
    data = resp2.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "duplicate" in data.get("message", "").lower() or "sku" in data.get("message", "").lower() or "conflicts" in data.get("message", "").lower()
# Archivo: sistema-api/test/test_products.py

def test_delete_nonexistent_product(client):
    nonexistent_product_id = 999999
    response = client.delete(f'/api/products/{nonexistent_product_id}') # URL corregida sin / final

    assert response.status_code == 404, "Debe devolver 404 Not Found al eliminar producto inexistente"
    data = response.get_json()
    # Tu endpoint de products.py, cuando product_service.delete_product (que llama a _logical_delete)
    # recibe un NotFoundException, devuelve:
    # jsonify({'success': False, 'message': str(e)}), 404
    assert data is not None, "La respuesta debe contener un cuerpo JSON"
    assert data.get("success") is False
    assert "not found" in data.get("message", "").lower() or "no encontrado" in data.get("message", "").lower()
def test_create_product_with_duplicate_sku_full_flow(client):
    # Asegurar que categoría y proveedor existen
    cat_resp = client.post('/api/categories/', json={"name": "Categoria para SKU Dup TC15"})
    assert cat_resp.status_code in (201, 409) # 409 si ya existe
    cat_id = cat_resp.get_json().get('category_id') if cat_resp.status_code == 201 else client.get('/api/categories/?name=Categoria para SKU Dup TC15').get_json()['data'][0]['id']

    sup_resp = client.post('/api/suppliers/', json={"name": "Proveedor para SKU Dup TC15"})
    assert sup_resp.status_code in (201, 409)
    sup_id = sup_resp.get_json().get('supplier_id') if sup_resp.status_code == 201 else client.get('/api/suppliers/?name=Proveedor para SKU Dup TC15').get_json()['data'][0]['id']

    sku_val = "SKU_DUPLICADO_TC15_FULL"
    product_payload_1 = {
        "sku": sku_val,
        "name": "Producto Original TC15",
        "category_id": cat_id,
        "supplier_id": sup_id,
        "unit_cost": 10.0,
        "unit_price": 20.0,
        "min_stock": 5
    }
    resp1 = client.post('/api/products/', json=product_payload_1)
    assert resp1.status_code == 201, f"Falló la creación del primer producto: {resp1.get_data(as_text=True)}"
    assert resp1.get_json()["success"] is True

    product_payload_2 = {
        "sku": sku_val, # Mismo SKU
        "name": "Producto Duplicado TC15",
        "category_id": cat_id,
        "supplier_id": sup_id,
        "unit_cost": 15.0,
        "unit_price": 25.0,
        "min_stock": 2
    }
    resp2 = client.post('/api/products/', json=product_payload_2)

    assert resp2.status_code == 409, "Debe rechazar producto con SKU duplicado (409 Conflict)"
    data = resp2.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "sku" in data.get("message", "").lower() or "conflicts" in data.get("message", "").lower()
def test_create_product_with_duplicate_sku_full_flow(client):
    # Asegurar que categoría y proveedor existen
    cat_resp = client.post('/api/categories/', json={"name": "Categoria para SKU Dup TC15"})
    assert cat_resp.status_code in (201, 409) # 409 si ya existe
    cat_id = cat_resp.get_json().get('category_id') if cat_resp.status_code == 201 else client.get('/api/categories/?name=Categoria para SKU Dup TC15').get_json()['data'][0]['id']

    sup_resp = client.post('/api/suppliers/', json={"name": "Proveedor para SKU Dup TC15"})
    assert sup_resp.status_code in (201, 409)
    sup_id = sup_resp.get_json().get('supplier_id') if sup_resp.status_code == 201 else client.get('/api/suppliers/?name=Proveedor para SKU Dup TC15').get_json()['data'][0]['id']

    sku_val = "SKU_DUPLICADO_TC15_FULL"
    product_payload_1 = {
        "sku": sku_val,
        "name": "Producto Original TC15",
        "category_id": cat_id,
        "supplier_id": sup_id,
        "unit_cost": 10.0,
        "unit_price": 20.0,
        "min_stock": 5
    }
    resp1 = client.post('/api/products/', json=product_payload_1)
    assert resp1.status_code == 201, f"Falló la creación del primer producto: {resp1.get_data(as_text=True)}"
    assert resp1.get_json()["success"] is True

    product_payload_2 = {
        "sku": sku_val, # Mismo SKU
        "name": "Producto Duplicado TC15",
        "category_id": cat_id,
        "supplier_id": sup_id,
        "unit_cost": 15.0,
        "unit_price": 25.0,
        "min_stock": 2
    }
    resp2 = client.post('/api/products/', json=product_payload_2)

    assert resp2.status_code == 409, "Debe rechazar producto con SKU duplicado (409 Conflict)"
    data = resp2.get_json()
    assert data is not None
    assert data.get("success") is False
    assert "sku" in data.get("message", "").lower() or "conflicts" in data.get("message", "").lower()
def test_create_product_rejects_large_payload(client, app): # app fixture para acceder a config
    # Configurar MAX_CONTENT_LENGTH para este test si es posible, o asegurar que es bajo.
    # Si no, este test prueba el límite del servidor WSGI o Flask por defecto.
    # app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # Ejemplo: 1MB
    # Esto debe hacerse antes de que el cliente se use para la petición.
    # Mejor hacerlo en la configuración de la app de prueba.

    # Un nombre muy grande para exceder un límite razonable (ej. si fuera 1MB)
    # Un string de 2MB puede ser demasiado para generar en memoria rápidamente en un test.
    # Vamos a usar un tamaño más manejable que igual debería ser rechazado si MAX_CONTENT_LENGTH se configura bajo.
    # Si MAX_CONTENT_LENGTH no está configurado, este test probablemente no dará 413.
    large_description = "A" * (1024 * 500) # 500KB de descripción
    payload = {
        "sku": "SKU-LARGE-PAYLOAD-TC16",
        "name": "Producto Payload Grande TC16",
        "description": large_description,
        "category_id": 1, # Asume que existe
        "supplier_id": 1, # Asume que existe
        "unit_cost": 1.0,
        "unit_price": 2.0
    }
    
    # Guardar el valor original de MAX_CONTENT_LENGTH si existe
    original_max_content_length = app.config.get('MAX_CONTENT_LENGTH')
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 256 # 256KB para el test
    
    response = client.post('/api/products/', json=payload)
    
    # Restaurar MAX_CONTENT_LENGTH
    if original_max_content_length is None:
        del app.config['MAX_CONTENT_LENGTH']
    else:
        app.config['MAX_CONTENT_LENGTH'] = original_max_content_length

    # Werkzeug devuelve 413 si se excede MAX_CONTENT_LENGTH
    # Si tu validación de campos ocurre antes (ej. longitud máxima de 'name'), podría ser 400.
    assert response.status_code == 413, f"Esperamos 413 Payload Too Large, pero recibimos {response.status_code}. Verifica MAX_CONTENT_LENGTH."
    # El cuerpo de la respuesta para 413 puede ser HTML por defecto de Werkzeug, no JSON.
    # data = response.get_json()
    # assert data is not None
    # assert "too large" in data.get("message","").lower()