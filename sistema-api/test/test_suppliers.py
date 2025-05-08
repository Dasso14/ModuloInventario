import pytest
import json
from unittest.mock import MagicMock, patch

from flask import Flask

# Import your blueprint and the service instance
# Adjust the import path based on your project structure
from app.api.suppliers import suppliers_bp, supplier_service

# Import exceptions
from app.utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException

# --- Fixtures ---
@pytest.fixture
def test_client():
    """Fixture for Flask test client."""
    app = Flask(__name__)
    # Register the blueprint with the correct URL prefix
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    with app.test_client() as client:
        yield client

# --- Mock Objects ---
class MockSupplier:
    """Helper mock class to simulate a Supplier model object."""
    # Add relevant supplier attributes as needed
    def __init__(self, id, name, email=None, phone=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
            # Add other attributes here
        }

# --- GET /api/suppliers Tests (list_suppliers) ---
@patch('app.api.suppliers.supplier_service.get_all_suppliers')
def test_list_suppliers_success_no_filters(mock_get_all, test_client):
    """Test listing suppliers successfully with no filters."""
    # Assuming the API doesn't currently parse filters/pagination/sorting
    mock_suppliers_list = [
        MockSupplier(id=1, name='Supplier A'),
        MockSupplier(id=2, name='Supplier B')
    ]
    mock_get_all.return_value = mock_suppliers_list

    response = test_client.get('/api/suppliers/')

    # Assert the service method was called with empty parameters
    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})

    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'data': [s.to_dict() for s in mock_suppliers_list]
    }

@patch('app.api.suppliers.supplier_service.get_all_suppliers')
def test_list_suppliers_database_error(mock_get_all, test_client):
    """Test listing suppliers handles database errors."""
    mock_get_all.side_effect = DatabaseException("DB error")
    response = test_client.get('/api/suppliers/')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.suppliers.supplier_service.get_all_suppliers')
def test_list_suppliers_unexpected_error(mock_get_all, test_client):
    """Test listing suppliers handles unexpected errors."""
    mock_get_all.side_effect = Exception("Something went wrong")
    response = test_client.get('/api/suppliers/')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}

# --- POST /api/suppliers Tests (create_supplier) ---
@patch('app.api.suppliers.supplier_service.create_supplier')
def test_create_supplier_success_minimal(mock_create, test_client):
    """Test creating a supplier successfully with minimal data."""
    # Assuming service validates required fields like 'name'
    mock_supplier_data = {'name': 'New Supplier'}
    mock_created_supplier = MockSupplier(id=1, name='New Supplier')
    mock_create.return_value = mock_created_supplier

    response = test_client.post('/api/suppliers/', json=mock_supplier_data)

    mock_create.assert_called_once_with(mock_supplier_data)
    assert response.status_code == 201
    assert response.json == {
        'success': True,
        'message': 'Supplier created successfully',
        'supplier_id': 1,
        'data': mock_created_supplier.to_dict()
    }

@patch('app.api.suppliers.supplier_service.create_supplier')
def test_create_supplier_success_full_data(mock_create, test_client):
    """Test creating a supplier successfully with full data."""
    mock_supplier_data = {
        'name': 'Full Supplier',
        'email': 'full@example.com',
        'phone': '123-456-7890'
    }
    mock_created_supplier = MockSupplier(id=2, **mock_supplier_data)
    mock_create.return_value = mock_created_supplier

    response = test_client.post('/api/suppliers/', json=mock_supplier_data)

    mock_create.assert_called_once_with(mock_supplier_data)
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['supplier_id'] == 2
    assert response.json['data']['name'] == 'Full Supplier'



# Note: API does not perform explicit validation for required fields or input types
# for supplier data. These are assumed to be handled by the service layer.
@patch('app.api.suppliers.supplier_service.create_supplier')
def test_create_supplier_service_validation_error(mock_create, test_client):
    """Test creating a supplier handles ValueError/TypeError from service (e.g., missing name)."""
    # Simulate service raising ValueError for missing required fields
    mock_create.side_effect = ValueError("Name is required")
    response = test_client.post('/api/suppliers/', json={}) # Missing name - send as dict

    # API validation (if not data) should pass a dict
    # Note: The original code had 'if not data:', which would return 400 here.
    # Assuming this check is refined to 'if not isinstance(data, dict)' like in other modules.
    # If 'if not data:' is kept, this test should expect 400 and service not called.
    # Let's assume the check is refined to 'if not isinstance(data, dict)'.
    # *Correction*: The provided suppliers.py *does* use `if not data:`.
    # So this test should expect 400 and service not called if passing an empty dict.
    # Let's update the test accordingly.

    # Test with missing required fields (API check - if not data)
    response = test_client.post('/api/suppliers/', json={}) # Empty dict is not data=True -> 400
    mock_create.assert_not_called()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid JSON data'} # API returns this message for not data

    # Simulate service raising TypeError (API passes valid dict)
    mock_create.reset_mock()
    mock_create.side_effect = TypeError("Invalid type for email")
    response = test_client.post('/api/suppliers/', json={'name': 'Test', 'email': 123}) # Invalid email type

    mock_create.assert_called_once() # API passes data to service
    assert response.status_code == 400 # API maps ValueError/TypeError to 400
    assert response.json == {'success': False, 'message': 'Invalid type for email'}


@patch('app.api.suppliers.supplier_service.create_supplier')
def test_create_supplier_conflict(mock_create, test_client):
    """Test creating a supplier when a conflict occurs (e.g., duplicate name/email)."""
    mock_create.side_effect = ConflictException("Supplier name already exists")
    response = test_client.post('/api/suppliers/', json={'name': 'Existing Supplier'})

    mock_create.assert_called_once()
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Supplier name already exists'}


@patch('app.api.suppliers.supplier_service.create_supplier')
def test_create_supplier_database_error(mock_create, test_client):
    """Test creating a supplier handles database errors."""
    mock_create.side_effect = DatabaseException("DB connection failed")
    response = test_client.post('/api/suppliers/', json={'name': 'Test Supplier'})

    mock_create.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB connection failed'}

@patch('app.api.suppliers.supplier_service.create_supplier')
def test_create_supplier_unexpected_error(mock_create, test_client):
    """Test creating a supplier handles unexpected errors."""
    mock_create.side_effect = Exception("Unexpected service error")
    response = test_client.post('/api/suppliers/', json={'name': 'Test Supplier'})

    mock_create.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- GET /api/suppliers/{id} Tests (get_supplier) ---
@patch('app.api.suppliers.supplier_service.get_supplier_by_id')
def test_get_supplier_success(mock_get_by_id, test_client):
    """Test getting a single supplier successfully."""
    mock_supplier = MockSupplier(id=1, name='Supplier A')
    mock_get_by_id.return_value = mock_supplier

    response = test_client.get('/api/suppliers/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 200
    assert response.json == {'success': True, 'data': mock_supplier.to_dict()}

@patch('app.api.suppliers.supplier_service.get_supplier_by_id')
def test_get_supplier_not_found(mock_get_by_id, test_client):
    """Test getting a single supplier that does not exist."""
    mock_get_by_id.side_effect = NotFoundException("Supplier not found")
    response = test_client.get('/api/suppliers/999')

    mock_get_by_id.assert_called_once_with(999)
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Supplier not found'}

@patch('app.api.suppliers.supplier_service.get_supplier_by_id')
def test_get_supplier_negative_id(mock_get_by_id, test_client):
    """
    Test getting a supplier with a negative ID in the URL.
    Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.get('/api/suppliers/-1')

    mock_get_by_id.assert_not_called() # Service should not be called
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
    # No specific JSON message expected here as Flask's default 404 is likely triggered


@patch('app.api.suppliers.supplier_service.get_supplier_by_id')
def test_get_supplier_database_error(mock_get_by_id, test_client):
    """Test getting a supplier handles database errors."""
    mock_get_by_id.side_effect = DatabaseException("DB error")
    response = test_client.get('/api/suppliers/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.suppliers.supplier_service.get_supplier_by_id')
def test_get_supplier_unexpected_error(mock_get_by_id, test_client):
    """Test getting a supplier handles unexpected errors."""
    mock_get_by_id.side_effect = Exception("Unexpected error")
    response = test_client.get('/api/suppliers/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- PUT/PATCH /api/suppliers/{id} Tests (update_supplier) ---
@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_success_put(mock_update, test_client):
    """Test updating a supplier successfully using PUT."""
    supplier_id = 1
    update_data = {'name': 'Updated Supplier A', 'email': 'updated@example.com'}
    mock_updated_supplier = MockSupplier(id=supplier_id, name='Updated Supplier A', email='updated@example.com')
    mock_update.return_value = mock_updated_supplier

    response = test_client.put(f'/api/suppliers/{supplier_id}', json=update_data)

    mock_update.assert_called_once_with(supplier_id, update_data)
    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'message': f'Supplier {supplier_id} updated successfully',
        'data': mock_updated_supplier.to_dict()
    }

@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_success_patch(mock_update, test_client):
    """Test updating a supplier successfully using PATCH (partial update)."""
    supplier_id = 1
    update_data = {'phone': '987-654-3210'} # Only update phone
    mock_updated_supplier = MockSupplier(id=supplier_id, name='Supplier A', phone='987-654-3210') # Simulate service return
    mock_update.return_value = mock_updated_supplier

    response = test_client.patch(f'/api/suppliers/{supplier_id}', json=update_data)

    mock_update.assert_called_once_with(supplier_id, update_data)
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == f'Supplier {supplier_id} updated successfully'
    assert response.json['data']['phone'] == '987-654-3210'


@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_invalid_id(mock_update, test_client):
    """
    Test updating a supplier with a negative ID in the URL.
     Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.put('/api/suppliers/-1', json={'name': 'Test'})

    mock_update.assert_not_called()
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
     # No specific JSON message expected here as Flask's default 404 is likely triggered


# Note: API does not perform explicit validation for field types or values in the payload.
# These are assumed to be handled by the service layer.
@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_service_validation_error(mock_update, test_client):
    """Test updating a supplier handles ValueError/TypeError from service."""
    supplier_id = 1
    # Simulate service raising TypeError for invalid data (e.g., bad type)
    mock_update.side_effect = TypeError("Invalid type for phone")
    # Send as dict, API passes it to service
    response = test_client.put(f'/api/suppliers/{supplier_id}', json={'phone': 12345}) # Invalid type

    mock_update.assert_called_once_with(supplier_id, {'phone': 12345}) # API passes data to service
    assert response.status_code == 400 # API maps ValueError/TypeError to 400
    assert response.json == {'success': False, 'message': 'Invalid type for phone'}


@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_not_found(mock_update, test_client):
    """Test updating a supplier that does not exist."""
    mock_update.side_effect = NotFoundException("Supplier not found")
    response = test_client.put('/api/suppliers/999', json={'name': 'Update'})

    mock_update.assert_called_once() # Service is called, raises error
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Supplier not found'}


@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_conflict(mock_update, test_client):
    """Test updating a supplier when a conflict occurs (e.g., duplicate name/email)."""
    mock_update.side_effect = ConflictException("Supplier name already exists")
    response = test_client.put('/api/suppliers/1', json={'name': 'Existing Supplier'})

    mock_update.assert_called_once()
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Supplier name already exists'}


@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_database_error(mock_update, test_client):
    """Test updating a supplier handles database errors."""
    mock_update.side_effect = DatabaseException("DB error")
    response = test_client.put('/api/suppliers/1', json={'name': 'Test'})

    mock_update.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}


@patch('app.api.suppliers.supplier_service.update_supplier')
def test_update_supplier_unexpected_error(mock_update, test_client):
    """Test updating a supplier handles unexpected errors."""
    mock_update.side_effect = Exception("Unexpected error")
    response = test_client.put('/api/suppliers/1', json={'name': 'Test'})

    mock_update.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- DELETE /api/suppliers/{id} Tests (delete_supplier) ---
@patch('app.api.suppliers.supplier_service.delete_supplier')
def test_delete_supplier_success(mock_delete, test_client):
    """Test deleting a supplier successfully."""
    supplier_id = 1
    mock_delete.return_value = True # Simulate service success

    response = test_client.delete(f'/api/suppliers/{supplier_id}')

    mock_delete.assert_called_once_with(supplier_id)
    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'message': f'Supplier {supplier_id} deleted successfully' # Check exact message
    }

@patch('app.api.suppliers.supplier_service.delete_supplier')
def test_delete_supplier_negative_id(mock_delete, test_client):
    """
    Test deleting a supplier with a negative ID in the URL.
     Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.delete('/api/suppliers/-1')

    mock_delete.assert_not_called()
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
    # No specific JSON message expected here as Flask's default 404 is likely triggered


@patch('app.api.suppliers.supplier_service.delete_supplier')
def test_delete_supplier_not_found(mock_delete, test_client):
    """Test deleting a supplier that does not exist."""
    mock_delete.side_effect = NotFoundException("Supplier not found")
    response = test_client.delete('/api/suppliers/999')

    mock_delete.assert_called_once_with(999)
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Supplier not found'}


@patch('app.api.suppliers.supplier_service.delete_supplier')
def test_delete_supplier_conflict(mock_delete, test_client):
    """Test deleting a supplier when a conflict prevents deletion (e.g., products linked)."""
    mock_delete.side_effect = ConflictException("Supplier is linked to products")
    response = test_client.delete('/api/suppliers/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 409 # API maps ConflictException to 409
    assert response.json == {'success': False, 'message': 'Supplier is linked to products'}


@patch('app.api.suppliers.supplier_service.delete_supplier')
def test_delete_supplier_service_returns_false(mock_delete, test_client):
    """Test deleting a supplier when the service returns False."""
    supplier_id = 1
    mock_delete.return_value = False # Simulate service returning False

    response = test_client.delete(f'/api/suppliers/{supplier_id}')

    mock_delete.assert_called_once_with(supplier_id)
    assert response.status_code == 500 # API returns 500 for service returning False
    assert response.json == {'success': False, 'message': f'Could not delete Supplier {supplier_id}'} # Check exact message


@patch('app.api.suppliers.supplier_service.delete_supplier')
def test_delete_supplier_database_error(mock_delete, test_client):
    """Test deleting a supplier handles database errors."""
    mock_delete.side_effect = DatabaseException("DB error")
    response = test_client.delete('/api/suppliers/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.suppliers.supplier_service.delete_supplier')
def test_delete_supplier_unexpected_error(mock_delete, test_client):
    """Test deleting a supplier handles unexpected errors."""
    mock_delete.side_effect = Exception("Unexpected error")
    response = test_client.delete('/api/suppliers/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}