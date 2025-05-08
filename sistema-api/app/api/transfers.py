# inventory_api/app/api/transfers.py

from flask import request, jsonify
from . import transfers_bp
from ..services import TransferService
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException
from datetime import datetime, date, timezone # Import timezone for consistent comparisons

transfer_service = TransferService()

# --- Helper Functions ---
def validate_int_param(param_value, param_name):
    """Helper to validate and convert query parameter to integer."""
    if param_value is None:
        return None # Allow parameter to be optional
    try:
        return int(param_value)
    except (ValueError, TypeError):
        # Raised on invalid string input, or if param_value was non-int like float or bool
        raise ValueError(f"Invalid {param_name}")

def validate_date_param(param_value, param_name):
    """Helper to validate and convert query parameter to datetime."""
    if param_value is None:
        return None # Allow parameter to be optional
    try:
        # Attempt to parse various ISO 8601 formats
        # fromisoformat handles Z and offsets, and returns timezone-aware datetimes
        dt_obj = datetime.fromisoformat(param_value.replace('Z', '+00:00'))
        # Optional: Convert to UTC naive if your application prefers naive datetimes
        # return dt_obj.replace(tzinfo=None) if dt_obj.tzinfo else dt_obj
        return dt_obj # Keep timezone-aware as fromisoformat returns it
    except (ValueError, TypeError):
        # Raised on invalid string format
        raise ValueError(f"Invalid {param_name} format")

# --- API Routes ---

@transfers_bp.route('/', methods=['POST'])
def create_transfer():
    """
    POST /api/transfers
    Registers a stock transfer between two locations.
    Expected JSON body: {"product_id": 1, "from_location_id": 1, "to_location_id": 2, "quantity": 5.0, "user_id": 1, "notes": "..."}
    """
    data = request.get_json()
    # Check if data is None (failed parse) or not a dictionary (e.g., JSON array or primitive)
    if not isinstance(data, dict):
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Basic validation of required fields existence (more detailed validation in service)
    required_fields = ['product_id', 'from_location_id', 'to_location_id', 'quantity', 'user_id']
    for field in required_fields:
        # Check if the key is missing OR if its value is explicitly None
        if field not in data or data[field] is None:
            return jsonify({'success': False, 'message': f'Missing or null required field: {field}'}), 400

    try:
        # Convert quantity to float/Decimal early
        # We already checked if data['quantity'] is None in the required_fields loop
        try:
             data['quantity'] = float(data['quantity'])
        except (ValueError, TypeError): # Catches non-numeric values like "abc" or boolean
             return jsonify({'success': False, 'message': 'Quantity must be a valid number'}), 400

        # Call the service to create the transfer (which creates transactions)
        # The service is responsible for validating product/location/user existence,
        # checking stock, preventing same-location transfers, etc.
        new_transfer = transfer_service.create_transfer(data)

        return jsonify({
            'success': True,
            'message': 'Transfer registered successfully',
            'transfer_id': new_transfer.id,
            'data': new_transfer.to_dict()
            }), 201

    # Consolidated exception handling based on service layer outcomes
    # Catch service validation errors like same locations
    except (ValueError, TypeError) as e: # Catches ValueErrors raised by the service
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e: # Product, Locations, or User not found by service
        return jsonify({'success': False, 'message': str(e)}), 404
    except InsufficientStockException as e: # Service indicates insufficient stock
         return jsonify({'success': False, 'message': str(e)}), 409 # Conflict due to insufficient stock
    except ConflictException as e: # Other potential conflicts from service/DB (e.g., concurrency)
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e: # Database errors from the service layer
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e: # Catch any unexpected errors
        # Log unexpected errors carefully in production
        print(f"An unexpected error occurred: {e}")
        # Depending on environment, you might not want to expose raw error
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@transfers_bp.route('/', methods=['GET'])
def list_transfers():
    """
    GET /api/transfers
    Gets a history of location transfers with filtering, pagination, and sorting.
    Used for reporting/history view.
    """
    try:
        filters = {}
        # Use helper functions for validation and conversion
        # validate_int_param and validate_date_param handle None for optional parameters
        filters['product_id'] = validate_int_param(request.args.get('productId'), 'productId')
        filters['from_location_id'] = validate_int_param(request.args.get('fromLocationId'), 'fromLocationId')
        filters['to_location_id'] = validate_int_param(request.args.get('toLocationId'), 'toLocationId')
        filters['user_id'] = validate_int_param(request.args.get('userId'), 'userId')
        filters['start_date'] = validate_date_param(request.args.get('startDate'), 'startDate')
        filters['end_date'] = validate_date_param(request.args.get('endDate'), 'endDate')

        # Remove None values from filters if parameters were not provided
        filters = {k: v for k, v in filters.items() if v is not None}


        pagination = {}
        # Use helper functions for validation and conversion
        page = validate_int_param(request.args.get('page'), 'page')
        limit = validate_int_param(request.args.get('limit'), 'limit')

        # Additional validation for pagination values after conversion
        if page is not None:
            if page < 1: # Basic validation for page number
                 return jsonify({'success': False, 'message': 'Page number must be positive'}), 400
            pagination['page'] = page
        if limit is not None:
            if limit < 1: # Basic validation for limit
                 return jsonify({'success': False, 'message': 'Limit must be positive'}), 400
            pagination['limit'] = limit


        sorting = {}
        sort_key = request.args.get('sortBy')
        if sort_key:
            # Add basic validation for sort_key if needed (e.g., allowed columns) - Not required by tests currently
            sort_order = request.args.get('order', 'desc').lower()
            if sort_order not in ['asc', 'desc']:
                 return jsonify({'success': False, 'message': 'Invalid sort order. Use "asc" or "desc"'}), 400
            sorting[sort_key] = sort_order

        # Call the service with the prepared parameters
        transfers = transfer_service.get_all_transfers(filters=filters, pagination=pagination, sorting=sorting)

        transfers_data = [t.to_dict() for t in transfers]

        return jsonify({'success': True, 'data': transfers_data}), 200

    # Catch exceptions from helper functions or service layer
    except (ValueError, TypeError) as e: # Catches errors from validate_int_param, validate_date_param
        return jsonify({'success': False, 'message': str(e)}), 400
    except DatabaseException as e: # Database errors from the service layer
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e: # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

@transfers_bp.route('/<int:transfer_id>', methods=['GET'])
def get_transfer(transfer_id):
    """
    GET /api/transfers/{transfer_id}
    Gets details for a specific transfer record by ID.
    """
    try:
        # Flask handles the conversion of transfer_id from URL to int
        # The service should raise NotFoundException if not found
        transfer = transfer_service.get_transfer_by_id(transfer_id)
        return jsonify({'success': True, 'data': transfer.to_dict()}), 200

    except NotFoundException as e: # Transfer not found by service
        return jsonify({'success': False, 'message': str(e)}), 404
    except (ValueError, TypeError) as e:
         # This exception is less likely to be hit for the URL path int parameter
         # but included for robustness if service raises it for some reason.
         return jsonify({'success': False, 'message': str(e)}), 400
    except DatabaseException as e: # Database errors from the service layer
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e: # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500