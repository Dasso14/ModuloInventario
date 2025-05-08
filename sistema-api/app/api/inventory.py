# inventory_api/app/api/inventory.py

# Import Blueprint along with request and jsonify
from flask import request, jsonify, Blueprint
# Import your backend service layer for inventory operations
# Assuming you have a service like InventoryService to handle database interactions
from . import inventory_bp
from ..services import InventoryService
from ..utils.exceptions import (
    NotFoundException,
    ConflictException,
    DatabaseException,
    InsufficientStockException, # Important for removals/transfers
)

# Define the blueprint for inventory routes


# Instantiate your InventoryService
# This service class should contain the logic to interact with your models/DB
inventory_service = InventoryService()

@inventory_bp.route('/add', methods=['POST','OPTIONS'])
def add_stock():
    """POST /api/inventory/add - Registers an inventory addition."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Validate required fields
    required_fields = ['product_id', 'location_id', 'quantity', 'user_id']
    # Also check that the values are not None if they are required
    if not all(field in data and data[field] is not None for field in required_fields):
         return jsonify({'success': False, 'message': f'Missing or null required fields: {", ".join(required_fields)}'}), 400

    try:
        # Ensure quantity is a positive number and can be converted to float
        try:
            quantity = float(data['quantity'])
        except (ValueError, TypeError):
             return jsonify({'success': False, 'message': 'Invalid quantity value'}), 400

        if quantity <= 0:
             return jsonify({'success': False, 'message': 'Quantity must be positive for addition'}), 400

        # Prepare data for the service layer
        transaction_data = {
            'product_id': data['product_id'],
            'location_id': data['location_id'],
            'quantity': quantity,
            'user_id': data['user_id'],
            'reference_number': data.get('reference_number'), # Optional field
            'notes': data.get('notes'), # Optional field
            'transaction_type': 'add' # Explicitly set type for the service
        }

        # Call the service to create the transaction and update stock levels
        # Assuming inventory_service.create_inventory_transaction handles the DB logic
        new_transaction = inventory_service.create_inventory_transaction(transaction_data)

        # Return success response
        return jsonify({
            'success': True,
            'message': 'Stock added successfully',
            'transaction_id': new_transaction.id, # Assuming the service returns the created object with an ID
            'data': new_transaction.to_dict() # Assuming your model/service returns a dict representation
            }), 201 # 201 Created

    except NotFoundException as e:
        # Handle cases where product_id, location_id, or user_id do not exist
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         # Handle database errors
         print(f"Database error during add_stock: {e}") # Log the error server-side
         return jsonify({'success': False, 'message': 'Database error occurred during stock addition'}), 500
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred in add_stock: {e}") # Log the error server-side
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@inventory_bp.route('/adjust', methods=['POST','OPTIONS'])
def adjust_stock():
    """POST /api/inventory/adjust - Registers an inventory adjustment."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Validate required fields for adjustment
    required_fields = ['product_id', 'location_id', 'quantity', 'user_id', 'notes']
    # Ensure all required fields are present and not None
    if not all(field in data and data[field] is not None for field in required_fields):
         return jsonify({'success': False, 'message': f'Missing or null required fields: {", ".join(required_fields)}'}), 400

    # Additional validation for notes for adjustments
    if not data.get('notes', '').strip():
        return jsonify({'success': False, 'message': 'Notes are required for stock adjustments to explain the reason.'}), 400

    try:
        # Ensure quantity is a valid number (can be positive or negative)
        try:
            quantity = float(data['quantity'])
        except (ValueError, TypeError):
             return jsonify({'success': False, 'message': 'Invalid quantity value'}), 400

        if quantity == 0:
             return jsonify({'success': False, 'message': 'Adjustment quantity cannot be zero'}), 400

        # Prepare data for the service layer
        transaction_data = {
            'product_id': data['product_id'],
            'location_id': data['location_id'],
            'quantity': quantity, # Quantity can be positive or negative
            'user_id': data['user_id'],
            'reference_number': data.get('reference_number'), # Optional field
            'notes': data['notes'], # Notes are mandatory here
            'transaction_type': 'adjust' # Explicitly set type for the service
        }

        # Call the service to create the transaction and update stock levels
        # The service needs to handle both positive and negative adjustments and potential InsufficientStockException
        new_transaction = inventory_service.create_inventory_transaction(transaction_data)

        # Return success response
        return jsonify({
            'success': True,
            'message': 'Stock adjusted successfully',
            'transaction_id': new_transaction.id, # Assuming the service returns the created object with an ID
            'data': new_transaction.to_dict() # Assuming your model/service returns a dict representation
            }), 201 # 201 Created

    except (ValueError, TypeError) as e:
        # Handle cases where quantity or IDs are not valid numbers
        return jsonify({'success': False, 'message': f'Invalid data type: {e}'}), 400
    except NotFoundException as e:
        # Handle cases where product_id, location_id, or user_id do not exist
        return jsonify({'success': False, 'message': str(e)}), 404
    except InsufficientStockException as e:
        # Handle cases where a negative adjustment would result in negative stock
        # Use 409 Conflict or 400 Bad Request depending on your API design philosophy
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         # Handle database errors
         print(f"Database error during adjust_stock: {e}") # Log the error server-side
         return jsonify({'success': False, 'message': 'Database error occurred during stock adjustment'}), 500
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred in adjust_stock: {e}") # Log the error server-side
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@inventory_bp.route('/remove', methods=['POST','OPTIONS'])
def remove_stock():
    """POST /api/inventory/remove - Registers an inventory removal."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Validate required fields for removal
    required_fields = ['product_id', 'location_id', 'quantity', 'user_id']
    if not all(field in data and data[field] is not None for field in required_fields):
         return jsonify({'success': False, 'message': f'Missing or null required fields: {", ".join(required_fields)}'}), 400

    try:
        # Ensure quantity is a positive number
        try:
            quantity = float(data['quantity'])
        except (ValueError, TypeError):
             return jsonify({'success': False, 'message': 'Invalid quantity value'}), 400

        if quantity <= 0:
             return jsonify({'success': False, 'message': 'Quantity must be positive for removal'}), 400

        # Prepare data for the service layer
        transaction_data = {
            'product_id': data['product_id'],
            'location_id': data['location_id'],
            'quantity': quantity,
            'user_id': data['user_id'],
            'reference_number': data.get('reference_number'), # Optional field
            'notes': data.get('notes'), # Optional field
            'transaction_type': 'remove' # Explicitly set type for the service
        }

        # Call the service to create the transaction and update stock levels
        # This needs to handle InsufficientStockException if stock goes below zero
        new_transaction = inventory_service.create_inventory_transaction(transaction_data)

        return jsonify({
            'success': True,
            'message': 'Stock removed successfully',
            'transaction_id': new_transaction.id,
            'data': new_transaction.to_dict()
            }), 201

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': f'Invalid data type: {e}'}), 400
    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except InsufficientStockException as e:
        # Handle cases where removal quantity is more than available stock
        return jsonify({'success': False, 'message': str(e)}), 409 # Or 400
    except DatabaseException as e:
         print(f"Database error during remove_stock: {e}")
         return jsonify({'success': False, 'message': 'Database error occurred during stock removal'}), 500
    except Exception as e:
        print(f"An unexpected error occurred in remove_stock: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@inventory_bp.route('/transfer', methods=['POST','OPTIONS'])
def transfer_stock():
    """POST /api/inventory/transfer - Registers a stock transfer."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Validate required fields for transfer
    required_fields = ['product_id', 'from_location_id', 'to_location_id', 'quantity', 'user_id']
    if not all(field in data and data[field] is not None for field in required_fields):
         return jsonify({'success': False, 'message': f'Missing or null required fields: {", ".join(required_fields)}'}), 400

    try:
        # Ensure quantity is a positive number
        try:
            quantity = float(data['quantity'])
        except (ValueError, TypeError):
             return jsonify({'success': False, 'message': 'Invalid quantity value'}), 400

        if quantity <= 0:
             return jsonify({'success': False, 'message': 'Quantity must be positive for transfer'}), 400

        # Ensure source and destination locations are different
        if data['from_location_id'] == data['to_location_id']:
             return jsonify({'success': False, 'message': 'Source and destination locations cannot be the same'}), 400

        # Prepare data for the service layer
        transfer_data = {
            'product_id': data['product_id'],
            'from_location_id': data['from_location_id'],
            'to_location_id': data['to_location_id'],
            'quantity': quantity,
            'user_id': data['user_id'],
            'notes': data.get('notes'), # Optional field
        }

        # Call the service to create the transfer record and associated transactions
        # Assuming inventory_service.create_location_transfer handles this complex logic
        new_transfer = inventory_service.create_location_transfer(transfer_data)

        return jsonify({
            'success': True,
            'message': 'Stock transferred successfully',
            'transfer_id': new_transfer.id, # Assuming the service returns the created transfer object
            'data': new_transfer.to_dict() # Assuming your model/service returns a dict representation
            }), 201

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': f'Invalid data type: {e}'}), 400
    except NotFoundException as e:
        # Handle cases where product_id, location_ids, or user_id do not exist
        return jsonify({'success': False, 'message': str(e)}), 404
    except InsufficientStockException as e:
        # Handle cases where removal quantity from the source location is more than available stock
        return jsonify({'success': False, 'message': str(e)}), 409 # Or 400
    except DatabaseException as e:
         print(f"Database error during transfer_stock: {e}")
         return jsonify({'success': False, 'message': 'Database error occurred during stock transfer'}), 500
    except Exception as e:
        print(f"An unexpected error occurred in transfer_stock: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500
