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
def test_create_product_success_full_data(mock_create, test_client):
    """Test creating a product successfully with full data."""
    mock_product_data = {
        'sku': 'FULL001',
        'name': 'Full Product',
        'description': 'Full description',
        'price': 10.50,
        'category_id': 1,
        'supplier_id': 10,
        'is_active': True
    }
    mock_created_product = MockProduct(id=2, **mock_product_data)
    mock_create.return_value = mock_created_product

    response = test_client.post('/api/products/', json=mock_product_data)

    mock_create.assert_called_once_with(mock_product_data)
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['product_id'] == 2
    assert response.json['data']['sku'] == 'FULL001'


@patch('app.api.products.product_service.create_product')
def test_create_product_invalid_json(mock_create, test_client):
    """Test creating a product with invalid JSON data (e.g., null or non-dict)."""
    # Sending 'null' as the body with JSON content type
    response = test_client.post(
        '/api/products/',
        data='null',
        content_type='application/json'
    )

    mock_create.assert_not_called() # Service should not be called
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}

    # Also test non-dict JSON (like a list)
    response = test_client.post('/api/products/', json=[{'sku': 'INV', 'name': 'Invalid'}])
    mock_create.assert_not_called()
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


# Note: API does not perform explicit validation for required fields or input types
# for product data. These are assumed to be handled by the service layer.
@patch('app.api.products.product_service.create_product')
def test_create_product_service_validation_error(mock_create, test_client):
    """Test creating a product handles ValueError/TypeError from service (e.g., missing fields)."""
    # Simulate service raising ValueError for missing required fields
    mock_create.side_effect = ValueError("SKU and Name are required")
    response = test_client.post('/api/products/', json={}) # Missing sku, name

    mock_create.assert_called_once() # API passes data to service
    assert response.status_code == 400 # API maps ValueError/TypeError to 400
    assert response.json == {'success': False, 'message': 'SKU and Name are required'}

    mock_create.reset_mock() # Reset for next assertion
    mock_create.side_effect = TypeError("Invalid type for price")
    response = test_client.post('/api/products/', json={'sku': 'TYPE', 'name': 'Type Error', 'price': 'ten'}) # Invalid price type
    mock_create.assert_called_once()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid type for price'}


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


# --- PUT/PATCH /api/products/{id} Tests (update_product) ---
@patch('app.api.products.product_service.update_product')
def test_update_product_success_put(mock_update, test_client):
    """Test updating a product successfully using PUT."""
    product_id = 1
    update_data = {'name': 'Updated Product A', 'price': 15.75}
    mock_updated_product = MockProduct(id=product_id, sku='SKU001', name='Updated Product A', price=15.75)
    mock_update.return_value = mock_updated_product

    response = test_client.put(f'/api/products/{product_id}', json=update_data)

    mock_update.assert_called_once_with(product_id, update_data)
    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'message': f'Product {product_id} updated successfully',
        'data': mock_updated_product.to_dict()
    }

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


@patch('app.api.products.product_service.update_product')
def test_update_product_invalid_json(mock_update, test_client):
    """Test updating a product with invalid JSON data (e.g., null or non-dict)."""
    product_id = 1
    # Sending 'null' as the body with JSON content type
    response = test_client.put(
        f'/api/products/{product_id}',
        data='null',
        content_type='application/json'
    )

    mock_update.assert_not_called() # Service should not be called
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}

    # Also test non-dict JSON (like a list)
    response = test_client.put(f'/api/products/{product_id}', json=[{'name': 'Invalid'}])
    mock_update.assert_not_called()
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


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


# API doesn't explicitly catch ConflictException for delete, it falls to generic handler
@patch('app.api.products.product_service.delete_product')
def test_delete_product_conflict(mock_delete, test_client):
    """Test deleting a product when a conflict prevents deletion (e.g., has stock/children)."""
    mock_delete.side_effect = ConflictException("Product has active stock")

    response = test_client.delete('/api/products/1')

    mock_delete.assert_called_once_with(1)
    # API's generic exception handler maps ConflictException to 409
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Product has active stock'}


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