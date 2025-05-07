# inventory_api/app/api/categories.py

from flask import request, jsonify
from . import categories_bp
from ..services import CategoryService
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException # Added InsufficientStockException back as it was missing

category_service = CategoryService()

@categories_bp.route('/', methods=['GET'])
def list_categories():
    """GET /api/categories - Lists categories."""
    try:
        filters = {}
        if 'name' in request.args:
             filters['name'] = request.args.get('name')
        if 'parent_id' in request.args:
             parent_id_str = request.args.get('parent_id')
             if parent_id_str.lower() == 'null' or parent_id_str == '':
                  filters['parent_id'] = None # Filter for root categories
             else:
                 try:
                    filters['parent_id'] = int(parent_id_str)
                 except ValueError:
                    return jsonify({'success': False, 'message': 'Invalid parent_id'}), 400


        pagination = {} # Add pagination parsing if needed
        sorting = {} # Add sorting parsing if needed

        categories = category_service.get_all_categories(filters=filters, pagination=pagination, sorting=sorting)
        categories_data = [cat.to_dict() for cat in categories]
        return jsonify({'success': True, 'data': categories_data}), 200

    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@categories_bp.route('/', methods=['POST'])
def create_category():
    """POST /api/categories - Creates a new category."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

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
    except NotFoundException as e: # Parent category not found
         return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # Duplicate name
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """GET /api/categories/{id} - Gets category details."""
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
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

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
    except ConflictException as e: # Duplicate name or cyclic parent
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """DELETE /api/categories/{id} - Deletes a category (physical)."""
    try:
        # This is a physical delete. Database constraints will prevent deleting if associated products/children exist.
        success = category_service.delete_category(category_id)

        if success:
             return jsonify({
                 'success': True,
                 'message': f'Category {category_id} deleted successfully'
                 }), 200
        else:
            # Should not happen if service returns True/raises exception correctly
             return jsonify({
                 'success': False,
                 'message': f'Could not delete Category {category_id}'
                 }), 500 # Or a more specific error


    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # Due to FK constraints (products or children linked)
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500