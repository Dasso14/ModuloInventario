# inventory_api/app/api/transactions.py

from flask import request, jsonify
from . import transactions_bp
from ..services import TransactionService, ReportService # Import ReportService for stock levels
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException # Added InsufficientStockException back as it was missing
from datetime import datetime, date

transaction_service = TransactionService()
report_service = ReportService() # Use ReportService for /api/stock-levels

@transactions_bp.route('/', methods=['POST'])
def create_transaction():
    """
    POST /api/transactions
    Registers a new inventory transaction (entrada, salida, ajuste).
    Expected JSON body: {"product_id": 1, "location_id": 1, "quantity": 10.5, "transaction_type": "entrada", "user_id": 1, ...}
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Basic validation of required fields existence (more detailed validation in service)
    required_fields = ['product_id', 'location_id', 'quantity', 'transaction_type', 'user_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

    try:
        # Convert quantity to float/Decimal early for validation
        try:
            data['quantity'] = float(data['quantity'])
        except (ValueError, TypeError):
             return jsonify({'success': False, 'message': 'Quantity must be a valid number'}), 400

        # Call the service to create the transaction
        new_transaction = transaction_service.create_transaction(data)

        return jsonify({
            'success': True,
            'message': 'Transaction registered successfully',
            'transaction_id': new_transaction.id,
            'data': new_transaction.to_dict()
            }), 201

    except (ValueError, TypeError) as e: # Invalid data format, invalid type enum
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e: # Product, Location, or User not found
        return jsonify({'success': False, 'message': str(e)}), 404
    except InsufficientStockException as e:
         return jsonify({'success': False, 'message': str(e)}), 409 # Conflict related to stock
    except ConflictException as e: # Other potential conflicts from service/DB
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@transactions_bp.route('/', methods=['GET'])
def list_transactions():
    """
    GET /api/transactions
    Gets a history of inventory transactions with filtering, pagination, and sorting.
    Used for reporting/history view.
    """
    try:
        filters = {}
        if 'productId' in request.args:
             try:
                filters['product_id'] = int(request.args.get('productId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid productId'}), 400
        if 'locationId' in request.args:
             try:
                filters['location_id'] = int(request.args.get('locationId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid locationId'}), 400
        if 'userId' in request.args:
             try:
                filters['user_id'] = int(request.args.get('userId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid userId'}), 400
        if 'type' in request.args:
             filters['transaction_type'] = request.args.get('type') # Service validates enum
        if 'startDate' in request.args:
             try:
                 # Assuming ISO 8601 format or similar. Needs robust parsing.
                 filters['start_date'] = datetime.fromisoformat(request.args.get('startDate'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid startDate format'}), 400
        if 'endDate' in request.args:
             try:
                 # Assuming ISO 8601 format or similar. Needs robust parsing.
                 filters['end_date'] = datetime.fromisoformat(request.args.get('endDate'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid endDate format'}), 400
        if 'reference_number' in request.args:
             filters['reference_number'] = request.args.get('reference_number')


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
            sort_order = request.args.get('order', 'desc') # Default sort for history is often desc
            sorting[sort_key] = sort_order


        transactions = transaction_service.get_all_transactions(filters=filters, pagination=pagination, sorting=sorting)

        transactions_data = [tx.to_dict() for tx in transactions]

        return jsonify({'success': True, 'data': transactions_data}), 200

    except (ValueError, TypeError) as e: # Catch validation errors from filter parsing/checking
        return jsonify({'success': False, 'message': str(e)}), 400
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    GET /api/transactions/{transaction_id}
    Gets details for a specific transaction by ID.
    """
    try:
        transaction = transaction_service.get_transaction_by_id(transaction_id)
        return jsonify({'success': True, 'data': transaction.to_dict()}), 200

    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# --- Stock Level Endpoint ---
@transactions_bp.route('/stock-levels', methods=['GET']) # Using the transactions blueprint as per description
def get_stock_levels_report():
    """
    GET /api/transactions/stock-levels (or ideally /api/stock-levels as per structure)
    Gets current stock levels for all product/location combinations.
    Filters can include: productId, locationId, categoryId, supplierId.
    """
    # Note: The endpoint description suggested /api/stock-levels, but the file structure lists it under transactions.
    # Let's stick to /api/transactions/stock-levels as per the file structure definition,
    # but ideally, it would be under a dedicated stock blueprint or the reports blueprint.
    # If you prefer /api/stock-levels, you'd need a new blueprint or define this route differently.

    try:
        filters = {}
        if 'productId' in request.args:
             try:
                filters['product_id'] = int(request.args.get('productId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid productId'}), 400
        if 'locationId' in request.args:
             try:
                filters['location_id'] = int(request.args.get('locationId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid locationId'}), 400
        if 'categoryId' in request.args:
             try:
                filters['category_id'] = int(request.args.get('categoryId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid categoryId'}), 400
        if 'supplierId' in request.args:
             try:
                filters['supplier_id'] = int(request.args.get('supplierId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid supplierId'}), 400

        pagination = {} # Add pagination parsing
        sorting = {} # Add sorting parsing


        stock_levels = report_service.get_stock_levels(filters=filters, pagination=pagination, sorting=sorting)

        stock_levels_data = [sl.to_dict() for sl in stock_levels]

        return jsonify({'success': True, 'data': stock_levels_data}), 200

    except (ValueError, TypeError) as e: # Catch validation errors from filter parsing/checking
        return jsonify({'success': False, 'message': str(e)}), 400
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500