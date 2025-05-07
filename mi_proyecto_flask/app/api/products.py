# inventory_api/app/api/products.py

from flask import request, jsonify
from . import products_bp
from ..services import ProductService
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException # Added InsufficientStockException back as it was missing
from datetime import datetime

# Instantiate the service
product_service = ProductService()

@products_bp.route('/', methods=['GET'])
def list_products():
    """
    GET /api/products
    Lists all products with optional filtering, pagination, and sorting.
    """
    try:
        # Parse query parameters for filtering, pagination, sorting
        filters = {}
        if 'sku' in request.args:
            filters['sku'] = request.args.get('sku')
        if 'name' in request.args:
            filters['name'] = request.args.get('name')
        if 'category_id' in request.args:
             try:
                filters['category_id'] = int(request.args.get('category_id'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid category_id'}), 400
        if 'supplier_id' in request.args:
             try:
                filters['supplier_id'] = int(request.args.get('supplier_id'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid supplier_id'}), 400
        if 'is_active' in request.args:
            # Convert string 'true'/'false' to boolean True/False
            is_active_str = request.args.get('is_active').lower()
            if is_active_str in ['true', '1']:
                filters['is_active'] = True
            elif is_active_str in ['false', '0']:
                filters['is_active'] = False
            # If not 'true' or 'false', it won't be added to filters, allowing fetching all states

        pagination = {}
        if 'page' in request.args:
            try:
                pagination['page'] = int(request.args.get('page'))
            except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid page number'}), 400
        if 'limit' in request.args:
            try:
                pagination['limit'] = int(request.args.get('limit'))
            except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid limit number'}), 400

        sorting = {}
        if 'sortBy' in request.args:
            sort_key = request.args.get('sortBy')
            sort_order = request.args.get('order', 'asc') # Default to ascending
            sorting[sort_key] = sort_order


        products = product_service.get_all_products(filters=filters, pagination=pagination, sorting=sorting)

        # Convert list of model objects to list of dictionaries
        products_data = [product.to_dict() for product in products]

        # In a real pagination scenario, you'd also return total items/pages
        # return jsonify({'success': True, 'data': products_data, 'pagination': {...}}), 200
        return jsonify({'success': True, 'data': products_data}), 200

    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        # Log the unexpected error
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@products_bp.route('/', methods=['POST'])
def create_product():
    """
    POST /api/products
    Creates a new product.
    Expected JSON body: {"sku": "...", "name": "...", ...}
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    try:
        new_product = product_service.create_product(data)
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': new_product.id,
            'data': new_product.to_dict() # Optionally return the created item
            }), 201 # 201 Created

    except (ValueError, TypeError) as e: # Catch validation errors from data parsing/checking
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e: # e.g., category_id or supplier_id not found
         return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # e.g., duplicate SKU
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    GET /api/products/{product_id}
    Gets details for a specific product by ID.
    """
    try:
        product = product_service.get_product_by_id(product_id)
        return jsonify({'success': True, 'data': product.to_dict()}), 200

    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@products_bp.route('/<int:product_id>', methods=['PUT', 'PATCH'])
def update_product(product_id):
    """
    PUT /api/products/{product_id} or PATCH /api/products/{product_id}
    Updates an existing product.
    Expected JSON body: {"name": "New Name", ...}
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    try:
        updated_product = product_service.update_product(product_id, data)
        return jsonify({
            'success': True,
            'message': f'Product {product_id} updated successfully',
            'data': updated_product.to_dict() # Optionally return the updated item
            }), 200

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # e.g., duplicate SKU during update
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    DELETE /api/products/{product_id}
    Deletes a product (logical delete).
    """
    try:
        success = product_service.delete_product(product_id) # Logical delete

        if success:
             return jsonify({
                 'success': True,
                 'message': f'Product {product_id} marked as inactive' # Reflects logical delete
                 }), 200
        else:
             # This branch might be hit if logical delete failed for some reason
             return jsonify({
                 'success': False,
                 'message': f'Could not mark Product {product_id} as inactive'
                 }), 500 # Or a more specific error code if applicable


    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500