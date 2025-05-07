# inventory_api/app/api/suppliers.py

from flask import request, jsonify
from . import suppliers_bp
from ..services import SupplierService
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException # Added InsufficientStockException back as it was missing

supplier_service = SupplierService()

@suppliers_bp.route('/', methods=['GET'])
def list_suppliers():
    """GET /api/suppliers - Lists suppliers."""
    try:
        filters = {} # Add filter parsing for supplier fields (name, email, etc.)
        pagination = {} # Add pagination parsing
        sorting = {} # Add sorting parsing

        suppliers = supplier_service.get_all_suppliers(filters=filters, pagination=pagination, sorting=sorting)
        suppliers_data = [sup.to_dict() for sup in suppliers]
        return jsonify({'success': True, 'data': suppliers_data}), 200

    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@suppliers_bp.route('/', methods=['POST'])
def create_supplier():
    """POST /api/suppliers - Creates a new supplier."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    try:
        new_supplier = supplier_service.create_supplier(data)
        return jsonify({
            'success': True,
            'message': 'Supplier created successfully',
            'supplier_id': new_supplier.id,
             'data': new_supplier.to_dict()
            }), 201

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except ConflictException as e: # e.g., duplicate name/email if constraints exist
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """GET /api/suppliers/{id} - Gets supplier details."""
    try:
        supplier = supplier_service.get_supplier_by_id(supplier_id)
        return jsonify({'success': True, 'data': supplier.to_dict()}), 200
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT', 'PATCH'])
def update_supplier(supplier_id):
    """PUT/PATCH /api/suppliers/{id} - Updates a supplier."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    try:
        updated_supplier = supplier_service.update_supplier(supplier_id, data)
        return jsonify({
            'success': True,
            'message': f'Supplier {supplier_id} updated successfully',
            'data': updated_supplier.to_dict()
            }), 200

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # e.g., duplicate name/email
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """DELETE /api/suppliers/{id} - Deletes a supplier (physical)."""
    try:
        # Physical delete. DB constraints will prevent if products are linked.
        success = supplier_service.delete_supplier(supplier_id)

        if success:
             return jsonify({
                 'success': True,
                 'message': f'Supplier {supplier_id} deleted successfully'
                 }), 200
        else:
             return jsonify({
                 'success': False,
                 'message': f'Could not delete Supplier {supplier_id}'
                 }), 500 # Or a more specific error


    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except ConflictException as e: # Due to FK constraints (products linked)
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500