# inventory_api/app/api/transfers.py

from flask import request, jsonify
from . import transfers_bp
from ..services import TransferService
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException # Added InsufficientStockException back as it was missing
from datetime import datetime, date

transfer_service = TransferService()

@transfers_bp.route('/', methods=['POST'])
def create_transfer():
    """
    POST /api/transfers
    Registers a stock transfer between two locations.
    Expected JSON body: {"product_id": 1, "from_location_id": 1, "to_location_id": 2, "quantity": 5.0, "user_id": 1, "notes": "..."}
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Basic validation of required fields existence (more detailed validation in service)
    required_fields = ['product_id', 'from_location_id', 'to_location_id', 'quantity', 'user_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

    try:
        # Convert quantity to float/Decimal early
        try:
            data['quantity'] = float(data['quantity'])
        except (ValueError, TypeError):
             return jsonify({'success': False, 'message': 'Quantity must be a valid number'}), 400

        # Call the service to create the transfer (which creates transactions)
        new_transfer = transfer_service.create_transfer(data)

        return jsonify({
            'success': True,
            'message': 'Transfer registered successfully',
            'transfer_id': new_transfer.id,
            'data': new_transfer.to_dict()
            }), 201

    except (ValueError, TypeError) as e: # Invalid data format, same locations
        return jsonify({'success': False, 'message': str(e)}), 400
    except NotFoundException as e: # Product, Locations, or User not found
        return jsonify({'success': False, 'message': str(e)}), 404
    except InsufficientStockException as e:
         return jsonify({'success': False, 'message': str(e)}), 409 # Conflict due to insufficient stock
    except ConflictException as e: # Other potential conflicts from service/DB
        return jsonify({'success': False, 'message': str(e)}), 409
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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
        if 'productId' in request.args:
             try:
                filters['product_id'] = int(request.args.get('productId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid productId'}), 400
        if 'fromLocationId' in request.args:
             try:
                filters['from_location_id'] = int(request.args.get('fromLocationId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid fromLocationId'}), 400
        if 'toLocationId' in request.args:
             try:
                filters['to_location_id'] = int(request.args.get('toLocationId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid toLocationId'}), 400
        if 'userId' in request.args:
             try:
                filters['user_id'] = int(request.args.get('userId'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid userId'}), 400
        if 'startDate' in request.args:
             try:
                 filters['start_date'] = datetime.fromisoformat(request.args.get('startDate'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid startDate format'}), 400
        if 'endDate' in request.args:
             try:
                 filters['end_date'] = datetime.fromisoformat(request.args.get('endDate'))
             except ValueError:
                 return jsonify({'success': False, 'message': 'Invalid endDate format'}), 400

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
            sort_order = request.args.get('order', 'desc')
            sorting[sort_key] = sort_order


        transfers = transfer_service.get_all_transfers(filters=filters, pagination=pagination, sorting=sorting)

        transfers_data = [t.to_dict() for t in transfers]

        return jsonify({'success': True, 'data': transfers_data}), 200

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

@transfers_bp.route('/<int:transfer_id>', methods=['GET'])
def get_transfer(transfer_id):
    """
    GET /api/transfers/{transfer_id}
    Gets details for a specific transfer record by ID.
    """
    try:
        transfer = transfer_service.get_transfer_by_id(transfer_id)
        return jsonify({'success': True, 'data': transfer.to_dict()}), 200

    except NotFoundException as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except DatabaseException as e:
         return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500