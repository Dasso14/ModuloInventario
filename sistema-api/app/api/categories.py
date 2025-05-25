from flask import request, jsonify
from . import categories_bp
from ..services import CategoryService
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException

category_service = CategoryService()


@categories_bp.route('/', methods=['GET'])
def list_categories():
    """GET /api/categories - Lists categories."""
    try:
        filters = {}
        if 'name' in request.args:
            name = request.args.get('name')
            if not isinstance(name, str) or not name.strip():
                return jsonify({'success': False, 'message': 'Invalid name filter'}), 400
            filters['name'] = name.strip()

        if 'parent_id' in request.args:
            parent_id_str = request.args.get('parent_id')
            if parent_id_str.lower() == 'null' or parent_id_str == '':
                filters['parent_id'] = None  # Filter for root categories
            else:
                try:
                    filters['parent_id'] = int(parent_id_str)
                except ValueError:
                    return jsonify({'success': False, 'message': 'Invalid parent_id'}), 400, {'Access-Control-Allow-Origin':'*'}

        pagination = {}  # Add pagination parsing if needed
        sorting = {}  # Add sorting parsing if needed

        categories = category_service.get_all_categories(filters=filters, pagination=pagination, sorting=sorting)
        categories_data = [cat.to_dict() for cat in categories]
        return jsonify({'success': True, 'data': categories_data}), 200,{'Access-Control-Allow-Origin':'*'}

    except DatabaseException as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@categories_bp.route('/', methods=['POST'])
def create_category():
    """POST /api/categories - Creates a new category."""
    data = request.get_json()
    # Check if get_json() returned None (which means parsing failed or wrong content type)
    if data is None: # <--- MODIFIED LINE
        return jsonify({'success': False, 'message': 'Invalid JSON data or incorrect Content-Type'}), 400

    # Validación adicional
    if 'name' not in data or not isinstance(data['name'], str) or not data['name'].strip():
        return jsonify({'success': False, 'message': 'Category name is required and must be a non-empty string'}), 400

    if 'parent_id' in data:
        if data['parent_id'] is not None and not isinstance(data['parent_id'], int):
            return jsonify({'success': False, 'message': 'parent_id must be an integer or null'}), 400
        if isinstance(data['parent_id'], int) and data['parent_id'] < 0:
            return jsonify({'success': False, 'message': 'parent_id must be non-negative'}), 400

    try:
        new_category = category_service.create_category(data)
        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'category_id': new_category.id,
            'data': new_category.to_dict()
        }), 201

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e:
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """GET /api/categories/{id} - Gets category details."""
    if category_id < 0:
        return jsonify({'success': False, 'message': 'category_id must be non-negative'}), 400

    try:
        category = category_service.get_category_by_id(category_id)
        return jsonify({'success': True, 'data': category.to_dict()}), 200
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@categories_bp.route('/<int:category_id>', methods=['PUT', 'PATCH'])
def update_category(category_id):
    """PUT/PATCH /api/categories/{id} - Updates a category."""
    if category_id < 0:
        return jsonify({'success': False, 'message': 'category_id must be non-negative'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Validaciones adicionales
    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return jsonify({'success': False, 'message': 'Category name must be a non-empty string'}), 400

    if 'parent_id' in data:
        if data['parent_id'] is not None and not isinstance(data['parent_id'], int):
            return jsonify({'success': False, 'message': 'parent_id must be an integer or null'}), 400
        if isinstance(data['parent_id'], int) and data['parent_id'] < 0:
            return jsonify({'success': False, 'message': 'parent_id must be non-negative'}), 400

    try:
        updated_category = category_service.update_category(category_id, data)
        return jsonify({
            'success': True,
            'message': f'Category {category_id} updated successfully',
            'data': updated_category.to_dict()
        }), 200

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e:
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """DELETE /api/categories/{id} - Deletes a category (physical)."""
    if category_id < 0:
        return jsonify({'success': False, 'message': 'category_id must be non-negative'}), 400

    try:
        success = category_service.delete_category(category_id)

        if success:
            return jsonify({
                'success': True,
                'message': f'Category {category_id} deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Could not delete Category {category_id}'
            }), 500

    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e:
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500
