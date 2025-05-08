import pytest
import json
from unittest.mock import MagicMock, patch

from flask import Flask

# Import your blueprint and the service instance
# Adjust the import path based on your project structure
from app.api.locations import locations_bp, location_service

# Import exceptions
from app.utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException

# --- Fixtures ---
@pytest.fixture
def test_client():
    """Fixture for Flask test client."""
    app = Flask(__name__)
    # Register the blueprint with the correct URL prefix
    app.register_blueprint(locations_bp, url_prefix='/api/locations')
    with app.test_client() as client:
        yield client

# --- Mock Objects ---
class MockLocation:
    """Helper mock class to simulate a Location model object."""
    def __init__(self, id, name, parent_id=None, is_active=True):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'is_active': self.is_active
        }

# --- GET /api/locations Tests (list_locations) ---
# Patch the specific service instance method used in the route
@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_success_no_filters(mock_get_all, test_client):
    """Test listing locations successfully with no filters."""
    # Simulate the service returning a list of mock locations
    mock_locations_list = [
        MockLocation(id=1, name='Warehouse A'),
        MockLocation(id=2, name='Shelf 1', parent_id=1)
    ]
    mock_get_all.return_value = mock_locations_list

    response = test_client.get('/api/locations/')

    # Assert the service method was called correctly
    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})

    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'data': [loc.to_dict() for loc in mock_locations_list]
    }

@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_success_with_name_filter(mock_get_all, test_client):
    """Test listing locations successfully with name filter."""
    mock_locations_list = [MockLocation(id=1, name='Warehouse A')]
    mock_get_all.return_value = mock_locations_list

    response = test_client.get('/api/locations/?name=Warehouse A')

    mock_get_all.assert_called_once_with(
        filters={'name': 'Warehouse A'},
        pagination={},
        sorting={}
    )
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['name'] == 'Warehouse A'


@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_success_with_is_active_filter(mock_get_all, test_client):
    """Test listing locations successfully with is_active filter."""
    mock_locations_list = [MockLocation(id=1, name='Active Loc', is_active=True)]
    mock_get_all.return_value = mock_locations_list

    # Test 'true'
    response = test_client.get('/api/locations/?is_active=true')
    mock_get_all.assert_called_once_with(filters={'is_active': True}, pagination={}, sorting={})
    assert response.status_code == 200

    mock_get_all.reset_mock() # Reset mock for next assertion

    # Test '1'
    response = test_client.get('/api/locations/?is_active=1')
    mock_get_all.assert_called_once_with(filters={'is_active': True}, pagination={}, sorting={})
    assert response.status_code == 200

    mock_get_all.reset_mock()

    # Test 'false'
    response = test_client.get('/api/locations/?is_active=false')
    mock_get_all.assert_called_once_with(filters={'is_active': False}, pagination={}, sorting={})
    assert response.status_code == 200

    mock_get_all.reset_mock()

    # Test '0'
    response = test_client.get('/api/locations/?is_active=0')
    mock_get_all.assert_called_once_with(filters={'is_active': False}, pagination={}, sorting={})
    assert response.status_code == 200

@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_invalid_is_active_filter(mock_get_all, test_client):
    """Test listing locations with invalid is_active filter."""
    # API code just doesn't add the filter if it doesn't match expected strings
    response = test_client.get('/api/locations/?is_active=yes')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={}) # Filter should be ignored
    assert response.status_code == 200


@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_success_filter_parent_id(mock_get_all, test_client):
    """Test listing locations filtering by parent_id (integer)."""
    mock_locations_list = [MockLocation(id=2, name='Shelf 1', parent_id=1)]
    mock_get_all.return_value = mock_locations_list

    response = test_client.get('/api/locations/?parent_id=1')

    mock_get_all.assert_called_once_with(
        filters={'parent_id': 1},
        pagination={},
        sorting={}
    )
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['parent_id'] == 1

@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_success_filter_parent_null(mock_get_all, test_client):
    """Test listing locations filtering for root locations (parent_id is null)."""
    mock_locations_list = [MockLocation(id=1, name='Warehouse A')]
    mock_get_all.return_value = mock_locations_list

    response = test_client.get('/api/locations/?parent_id=null')

    mock_get_all.assert_called_once_with(
        filters={'parent_id': None},
        pagination={},
        sorting={}
    )
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['parent_id'] is None

@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_success_filter_parent_empty_string(mock_get_all, test_client):
    """Test listing locations filtering for root locations (parent_id is empty string)."""
    mock_locations_list = [MockLocation(id=1, name='Warehouse A')]
    mock_get_all.return_value = mock_locations_list

    response = test_client.get('/api/locations/?parent_id=') # Empty string query param

    mock_get_all.assert_called_once_with(
        filters={'parent_id': None},
        pagination={},
        sorting={}
    )
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['parent_id'] is None


@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_invalid_parent_id_filter(mock_get_all, test_client):
    """Test listing locations with invalid parent_id filter (non-integer string)."""
    response = test_client.get('/api/locations/?parent_id=abc')

    mock_get_all.assert_not_called() # Service should not be called due to validation
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid parent_id'}

# Note: There is no API-level validation for negative parent_id in list_locations.
# If a negative number string was sent, it would raise ValueError in int(), caught by the API.
# If a negative integer was somehow passed directly (not from query string), it would go to the service.


@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_database_error(mock_get_all, test_client):
    """Test listing locations handles database errors."""
    mock_get_all.side_effect = DatabaseException("DB error")

    response = test_client.get('/api/locations/')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.locations.location_service.get_all_locations')
def test_list_locations_unexpected_error(mock_get_all, test_client):
    """Test listing locations handles unexpected errors."""
    mock_get_all.side_effect = Exception("Something went wrong")

    response = test_client.get('/api/locations/')

    mock_get_all.assert_called_once_with(filters={}, pagination={}, sorting={})
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- POST /api/locations Tests (create_location) ---
@patch('app.api.locations.location_service.create_location')
def test_create_location_success_minimal(mock_create, test_client):
    """Test creating a location successfully with minimal data."""
    # Assuming service validates required fields like 'name'
    mock_location_data = {'name': 'New Location'}
    mock_created_location = MockLocation(id=1, name='New Location')
    mock_create.return_value = mock_created_location

    response = test_client.post('/api/locations/', json=mock_location_data)

    mock_create.assert_called_once_with(mock_location_data)
    assert response.status_code == 201
    assert response.json == {
        'success': True,
        'message': 'Location created successfully',
        'location_id': 1,
        'data': mock_created_location.to_dict()
    }

@patch('app.api.locations.location_service.create_location')
def test_create_location_success_with_parent(mock_create, test_client):
    """Test creating a location successfully with a parent_id."""
    mock_location_data = {'name': 'Sub Location', 'parent_id': 1}
    mock_created_location = MockLocation(id=2, name='Sub Location', parent_id=1)
    mock_create.return_value = mock_created_location

    response = test_client.post('/api/locations/', json=mock_location_data)

    mock_create.assert_called_once_with(mock_location_data)
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['location_id'] == 2
    assert response.json['data']['parent_id'] == 1


@patch('app.api.locations.location_service.create_location')
def test_create_location_success_with_null_parent(mock_create, test_client):
    """Test creating a location successfully with parent_id explicitly null."""
    mock_location_data = {'name': 'Another Root Location', 'parent_id': None}
    mock_created_location = MockLocation(id=3, name='Another Root Location', parent_id=None)
    mock_create.return_value = mock_created_location

    response = test_client.post('/api/locations/', json=mock_location_data)

    mock_create.assert_called_once_with(mock_location_data)
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['location_id'] == 3
    assert response.json['data']['parent_id'] is None


@patch('app.api.locations.location_service.create_location')
def test_create_location_invalid_json(mock_create, test_client):
    """Test creating a location with invalid JSON data (e.g., null or non-dict)."""
    # Sending 'null' as the body with JSON content type
    # This should result in request.get_json() returning None,
    # triggering the 'if not data' check.
    response = test_client.post(
        '/api/locations/',
        data='null',
        content_type='application/json'
    )

    mock_create.assert_not_called() # Service should not be called
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}

    # Also test non-dict JSON (like a list)
    response = test_client.post('/api/locations/', json=[{'name': 'Invalid'}])
    mock_create.assert_not_called()
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


# Note: API does not perform explicit validation for missing 'name' or invalid types
# for other fields. These are assumed to be handled by the service layer.
@patch('app.api.locations.location_service.create_location')
def test_create_location_service_validation_error(mock_create, test_client):
    """Test creating a location handles ValueError/TypeError from service."""
    # Simulate service raising ValueError for missing required fields or invalid types
    mock_create.side_effect = ValueError("Name is required")
    response = test_client.post('/api/locations/', json={}) # Missing name

    mock_create.assert_called_once() # API passes data to service
    assert response.status_code == 400 # API maps ValueError/TypeError to 400
    assert response.json == {'success': False, 'message': 'Name is required'}

    mock_create.reset_mock() # Reset for next assertion
    mock_create.side_effect = TypeError("Invalid type for field")
    response = test_client.post('/api/locations/', json={'name': 'Test', 'parent_id': 'abc'}) # Invalid parent_id type
    mock_create.assert_called_once()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid type for field'}


@patch('app.api.locations.location_service.create_location')
def test_create_location_parent_not_found(mock_create, test_client):
    """Test creating a location when the parent location is not found."""
    mock_create.side_effect = NotFoundException("Parent location not found")
    response = test_client.post('/api/locations/', json={'name': 'Test', 'parent_id': 999})

    mock_create.assert_called_once() # Service is called, raises error
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Parent location not found'}


@patch('app.api.locations.location_service.create_location')
def test_create_location_conflict(mock_create, test_client):
    """Test creating a location when a conflict occurs (e.g., duplicate name, cyclic parent)."""
    mock_create.side_effect = ConflictException("Location name already exists")
    response = test_client.post('/api/locations/', json={'name': 'Existing Location'})

    mock_create.assert_called_once()
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Location name already exists'}


@patch('app.api.locations.location_service.create_location')
def test_create_location_database_error(mock_create, test_client):
    """Test creating a location handles database errors."""
    mock_create.side_effect = DatabaseException("DB connection failed")
    response = test_client.post('/api/locations/', json={'name': 'Test'})

    mock_create.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB connection failed'}

@patch('app.api.locations.location_service.create_location')
def test_create_location_unexpected_error(mock_create, test_client):
    """Test creating a location handles unexpected errors."""
    mock_create.side_effect = Exception("Unexpected service error")
    response = test_client.post('/api/locations/', json={'name': 'Test'})

    mock_create.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- GET /api/locations/{id} Tests (get_location) ---
@patch('app.api.locations.location_service.get_location_by_id')
def test_get_location_success(mock_get_by_id, test_client):
    """Test getting a single location successfully."""
    mock_location = MockLocation(id=1, name='Warehouse A', parent_id=None)
    mock_get_by_id.return_value = mock_location

    response = test_client.get('/api/locations/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 200
    assert response.json == {'success': True, 'data': mock_location.to_dict()}

@patch('app.api.locations.location_service.get_location_by_id')
def test_get_location_not_found(mock_get_by_id, test_client):
    """Test getting a single location that does not exist."""
    mock_get_by_id.side_effect = NotFoundException("Location not found")

    response = test_client.get('/api/locations/999')

    mock_get_by_id.assert_called_once_with(999)
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}

@patch('app.api.locations.location_service.get_location_by_id')
def test_get_location_negative_id(mock_get_by_id, test_client):
    """
    Test getting a location with a negative ID in the URL.
    Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.get('/api/locations/-1')

    mock_get_by_id.assert_not_called() # Service should not be called
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
    # No specific JSON message expected here as Flask's default 404 is likely triggered

@patch('app.api.locations.location_service.get_location_by_id')
def test_get_location_database_error(mock_get_by_id, test_client):
    """Test getting a location handles database errors."""
    mock_get_by_id.side_effect = DatabaseException("DB error")

    response = test_client.get('/api/locations/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.locations.location_service.get_location_by_id')
def test_get_location_unexpected_error(mock_get_by_id, test_client):
    """Test getting a location handles unexpected errors."""
    mock_get_by_id.side_effect = Exception("Unexpected error")

    response = test_client.get('/api/locations/1')

    mock_get_by_id.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}

# --- PUT/PATCH /api/locations/{id} Tests (update_location) ---
@patch('app.api.locations.location_service.update_location')
def test_update_location_success_put(mock_update, test_client):
    """Test updating a location successfully using PUT."""
    location_id = 1
    update_data = {'name': 'Updated Warehouse', 'is_active': False}
    mock_updated_location = MockLocation(id=location_id, name='Updated Warehouse', is_active=False)
    mock_update.return_value = mock_updated_location

    response = test_client.put(f'/api/locations/{location_id}', json=update_data)

    mock_update.assert_called_once_with(location_id, update_data)
    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'message': f'Location {location_id} updated successfully',
        'data': mock_updated_location.to_dict()
    }

@patch('app.api.locations.location_service.update_location')
def test_update_location_success_patch(mock_update, test_client):
    """Test updating a location successfully using PATCH (partial update)."""
    location_id = 1
    update_data = {'name': 'Only Name Updated'} # Only update name
    # Simulate service return, assuming it merges changes
    mock_updated_location = MockLocation(id=location_id, name='Only Name Updated', is_active=True, parent_id=None)
    mock_update.return_value = mock_updated_location

    response = test_client.patch(f'/api/locations/{location_id}', json=update_data)

    mock_update.assert_called_once_with(location_id, update_data)
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == f'Location {location_id} updated successfully'
    assert response.json['data']['name'] == 'Only Name Updated' # Check updated data

@patch('app.api.locations.location_service.update_location')
def test_update_location_success_patch_parent_null(mock_update, test_client):
    """Test patching a location successfully to set parent_id to null."""
    location_id = 2
    update_data = {'parent_id': None}
    mock_updated_location = MockLocation(id=location_id, name='Was Sub', parent_id=None)
    mock_update.return_value = mock_updated_location

    response = test_client.patch(f'/api/locations/{location_id}', json=update_data)

    mock_update.assert_called_once_with(location_id, update_data)
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['data']['parent_id'] is None


@patch('app.api.locations.location_service.update_location')
def test_update_location_invalid_id(mock_update, test_client):
    """
    Test updating a location with a negative ID in the URL.
     Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.put('/api/locations/-1', json={'name': 'Test'})

    mock_update.assert_not_called()
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
     # No specific JSON message expected here as Flask's default 404 is likely triggered


@patch('app.api.locations.location_service.update_location')
def test_update_location_invalid_json(mock_update, test_client):
    """Test updating a location with invalid JSON data (e.g., null or non-dict)."""
    location_id = 1
    # Sending 'null' as the body with JSON content type
    # This should result in request.get_json() returning None,
    # triggering the 'if not data' check.
    response = test_client.put(
        f'/api/locations/{location_id}',
        data='null',
        content_type='application/json'
    )

    mock_update.assert_not_called() # Service should not be called
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}

    # Also test non-dict JSON (like a list)
    response = test_client.put(f'/api/locations/{location_id}', json=[{'name': 'Invalid'}])
    mock_update.assert_not_called()
    assert response.status_code == 400 # Expecting 400 from API validation
    assert response.json == {'success': False, 'message': 'Invalid JSON data'}


# Note: API does not perform explicit validation for field types or values in the payload.
# These are assumed to be handled by the service layer.
@patch('app.api.locations.location_service.update_location')
def test_update_location_service_validation_error(mock_update, test_client):
    """Test updating a location handles ValueError/TypeError from service."""
    location_id = 1
    # Simulate service raising ValueError for invalid data combination
    mock_update.side_effect = ValueError("Cannot set location as parent of itself")
    response = test_client.put(f'/api/locations/{location_id}', json={'parent_id': location_id}) # Example invalid data

    mock_update.assert_called_once() # API passes data to service
    assert response.status_code == 400 # API maps ValueError/TypeError to 400
    assert response.json == {'success': False, 'message': 'Cannot set location as parent of itself'}

    mock_update.reset_mock()
    mock_update.side_effect = TypeError("Invalid type for field")
    response = test_client.put(f'/api/locations/{location_id}', json={'is_active': 'yes'}) # Invalid type
    mock_update.assert_called_once()
    assert response.status_code == 400
    assert response.json == {'success': False, 'message': 'Invalid type for field'}


@patch('app.api.locations.location_service.update_location')
def test_update_location_not_found(mock_update, test_client):
    """Test updating a location that does not exist or whose parent does not exist."""
    mock_update.side_effect = NotFoundException("Location not found")
    response = test_client.put('/api/locations/999', json={'name': 'Update'})

    mock_update.assert_called_once() # Service is called, raises error
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}

# Note: If the service raises NotFoundException due to a parent_id not found,
# the API handler catches it and returns 404, which is correctly covered by test_update_location_not_found's pattern.


@patch('app.api.locations.location_service.update_location')
def test_update_location_conflict(mock_update, test_client):
    """Test updating a location when a conflict occurs (e.g., duplicate name, cyclic parent)."""
    mock_update.side_effect = ConflictException("Location name already exists")
    response = test_client.put('/api/locations/1', json={'name': 'Existing Location'})

    mock_update.assert_called_once()
    assert response.status_code == 409
    assert response.json == {'success': False, 'message': 'Location name already exists'}


@patch('app.api.locations.location_service.update_location')
def test_update_location_database_error(mock_update, test_client):
    """Test updating a location handles database errors."""
    mock_update.side_effect = DatabaseException("DB error")
    response = test_client.put('/api/locations/1', json={'name': 'Test'})

    mock_update.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}


@patch('app.api.locations.location_service.update_location')
def test_update_location_unexpected_error(mock_update, test_client):
    """Test updating a location handles unexpected errors."""
    mock_update.side_effect = Exception("Unexpected error")
    response = test_client.put('/api/locations/1', json={'name': 'Test'})

    mock_update.assert_called_once()
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}


# --- DELETE /api/locations/{id} Tests (delete_location) ---
@patch('app.api.locations.location_service.delete_location')
def test_delete_location_success(mock_delete, test_client):
    """Test deleting (marking inactive) a location successfully."""
    location_id = 1
    mock_delete.return_value = True # Simulate service success

    response = test_client.delete(f'/api/locations/{location_id}')

    mock_delete.assert_called_once_with(location_id)
    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'message': f'Location {location_id} marked as inactive' # Check exact message
    }

@patch('app.api.locations.location_service.delete_location')
def test_delete_location_invalid_id(mock_delete, test_client):
    """
    Test deleting a location with a negative ID in the URL.
     Note: Flask routing might return 404 before the route handler is executed
          for negative integers in URL converters, depending on the environment.
          We assert 404 based on this likely routing behavior.
    """
    response = test_client.delete('/api/locations/-1')

    mock_delete.assert_not_called()
    # Asserting 404 based on the likely Flask routing behavior
    assert response.status_code == 404
    # No specific JSON message expected here as Flask's default 404 is likely triggered


@patch('app.api.locations.location_service.delete_location')
def test_delete_location_not_found(mock_delete, test_client):
    """Test deleting a location that does not exist."""
    mock_delete.side_effect = NotFoundException("Location not found")

    response = test_client.delete('/api/locations/999')

    mock_delete.assert_called_once_with(999)
    assert response.status_code == 404
    assert response.json == {'success': False, 'message': 'Location not found'}


# Note: API doesn't explicitly handle ConflictException for delete,
# but the service might raise it (e.g., if location has stock/children and physical delete was intended).
# The API's generic exception handler would catch it. Let's add a test for this mapping.
@patch('app.api.locations.location_service.delete_location')
def test_delete_location_conflict(mock_delete, test_client):
    """Test deleting a location when a conflict prevents deletion."""
    mock_delete.side_effect = ConflictException("Location has active stock")

    response = test_client.delete('/api/locations/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 409 # API maps ConflictException to 409
    assert response.json == {'success': False, 'message': 'Location has active stock'}


@patch('app.api.locations.location_service.delete_location')
def test_delete_location_service_returns_false(mock_delete, test_client):
    """Test deleting a location when the service returns False."""
    location_id = 1
    mock_delete.return_value = False # Simulate service returning False

    response = test_client.delete(f'/api/locations/{location_id}')

    mock_delete.assert_called_once_with(location_id)
    assert response.status_code == 500 # API returns 500 for service returning False
    assert response.json == {'success': False, 'message': f'Could not mark Location {location_id} as inactive'} # Check exact message


@patch('app.api.locations.location_service.delete_location')
def test_delete_location_database_error(mock_delete, test_client):
    """Test deleting a location handles database errors."""
    mock_delete.side_effect = DatabaseException("DB error")

    response = test_client.delete('/api/locations/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'DB error'}

@patch('app.api.locations.location_service.delete_location')
def test_delete_location_unexpected_error(mock_delete, test_client):
    """Test deleting a location handles unexpected errors."""
    mock_delete.side_effect = Exception("Unexpected error")

    response = test_client.delete('/api/locations/1')

    mock_delete.assert_called_once_with(1)
    assert response.status_code == 500
    assert response.json == {'success': False, 'message': 'An internal error occurred'}