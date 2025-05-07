# inventory_api/app/api/locations.py

from flask import request, jsonify
from . import locations_bp
from ..services import LocationService
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException # Added InsufficientStockException back as it was missing


location_service = LocationService()

@locations_bp.route('/', methods=['GET'])
def list_locations():
    """GET /api/locations - Lists locations."""
    try:
        filters = {}
        if 'name' in request.args:
             filters['name'] = request.args.get('name')
        if 'is_active' in request.args:
             is_active_str = request.args.get('is_active').lower()
             if is_active_str in ['true', '1']:
                  filters['is_active'] = True
             elif is_active_str in ['false', '0']:
                  filters['is_active'] = False
        if 'parent_id' in request.args: # Maps to parent_location in DB
             parent_id_str = request.args.get('parent_id')
             if parent_id_str.lower() == 'null' or parent_id_str == '':
                  filters['parent_id'] = None # Filter for root locations
             else:
                 try:
                    filters['parent_id'] = int(parent_id_str)
                 except ValueError:
                    return jsonify({'success': False, 'message': 'Invalid parent_id'}), 400


        pagination = {} # Add pagination parsing
        sorting = {} # Add sorting parsing


        locations = location_service.get_all_locations(filters=filters, pagination=pagination, sorting=sorting)
        locations_data = [loc.to_dict() for loc in locations]
        return jsonify({'success': True, 'data': locations_data}), 200

    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@locations_bp.route('/', methods=['POST'])
def create_location():
    """POST /api/locations - Creates a new location."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    try:
        new_location = location_service.create_location(data)
        return jsonify({
            'success': True,
            'message': 'Location created successfully',
            'location_id': new_location.id,
            'data': new_location.to_dict()
            }), 201

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e: # Parent location not found
         return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # Duplicate name, cyclic parent
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@locations_bp.route('/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """GET /api/locations/{id} - Gets location details."""
    try:
        location = location_service.get_location_by_id(location_id)
        return jsonify({'success': True, 'data': location.to_dict()}), 200
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@locations_bp.route('/<int:location_id>', methods=['PUT', 'PATCH'])
def update_location(location_id):
    """PUT/PATCH /api/locations/{id} - Updates a location."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    try:
        updated_location = location_service.update_location(location_id, data)
        return jsonify({
            'success': True,
            'message': f'Location {location_id} updated successfully',
            'data': updated_location.to_dict()
            }), 200

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # Duplicate name, cyclic parent
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@locations_bp.route('/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """DELETE /api/locations/{id} - Deletes a location (logical)."""
    try:
        # Logical delete (set is_active=False)
        success = location_service.delete_location(location_id)

        if success:
             return jsonify({
                 'success': True,
                 'message': f'Location {location_id} marked as inactive'
                 }), 200
        else:
             return jsonify({
                 'success': False,
                 'message': f'Could not mark Location {location_id} as inactive'
                 }), 500 # Or a more specific error


    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500