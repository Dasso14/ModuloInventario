# inventory_api/app/services/transfer_service.py

from .base_service import BaseService
from ..models import LocationTransfer, Product, Location, User, InventoryTransaction, StockLevel
from ..utils.enums import TransactionType
from ..db import db
from ..utils.exceptions import NotFoundException, ConflictException, InsufficientStockException, DatabaseException
from sqlalchemy.exc import OperationalError,IntegrityError
from datetime import datetime
from .transaction_service import TransactionService


class TransferService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = LocationTransfer
        self.transaction_service = TransactionService() # Use the transaction service for transaction creation

    def get_all_transfers(self, filters=None, pagination=None, sorting=None):
        """
        Gets all location transfers with optional filtering, pagination, and sorting.
        Filters can include: product_id, from_location_id, to_location_id, user_id,
        start_date, end_date.
        """
        query = self.model.query.join(Product).join(Location, self.model.from_location_id == Location.id).join(Location, self.model.to_location_id == Location.id).outerjoin(User)

        # Apply filters
        if filters:
            if 'product_id' in filters:
                 query = query.filter(self.model.product_id == filters['product_id'])
            if 'from_location_id' in filters:
                 query = query.filter(self.model.from_location_id == filters['from_location_id'])
            if 'to_location_id' in filters:
                 query = query.filter(self.model.to_location_id == filters['to_location_id'])
            if 'user_id' in filters:
                 query = query.filter(self.model.user_id == filters['user_id'])
            if 'start_date' in filters:
                 query = query.filter(self.model.transfer_date >= filters['start_date'])
            if 'end_date' in filters:
                 query = query.filter(self.model.transfer_date <= filters['end_date'])
            # Add more filters

        # Apply sorting
        if sorting:
             for sort_key, sort_order in sorting.items():
                 # Handle sorting by joined fields
                if sort_key == 'product_name':
                    column = Product.name
                elif sort_key == 'from_location_name':
                    # Need to alias Location table for sorting on specific join
                    from_loc_alias = db.aliased(Location, name='from_location')
                    query = query.join(from_loc_alias, self.model.from_location_id == from_loc_alias.id)
                    column = from_loc_alias.name
                elif sort_key == 'to_location_name':
                    # Need to alias Location table for sorting on specific join
                    to_loc_alias = db.aliased(Location, name='to_location')
                    query = query.join(to_loc_alias, self.model.to_location_id == to_loc_alias.id)
                    column = to_loc_alias.name
                elif sort_key == 'user_name':
                    column = User.username
                elif hasattr(self.model, sort_key): # Sorting on direct transfer fields
                    column = getattr(self.model, sort_key)
                else:
                    continue # Skip unknown sort keys

                if sort_order.lower() == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

        # Default sorting
        if not sorting:
             query = query.order_by(db.desc(self.model.transfer_date))

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
            return items
        else:
            return query.all()

    def get_transfer_by_id(self, transfer_id):
        """Gets a single transfer record by its ID."""
        transfer = self.model.query.options(
            db.joinedload(LocationTransfer.product),
            db.joinedload(LocationTransfer.from_location),
            db.joinedload(LocationTransfer.to_location),
            db.joinedload(LocationTransfer.user)
        ).filter(self.model.id == transfer_id).first()

        if transfer is None:
             raise NotFoundException(f"LocationTransfer with ID {transfer_id} not found.")
        return transfer


    def create_transfer(self, data):
        """
        Initiates a stock transfer between locations.
        This replicates the logic of the transfer_stock stored procedure:
        Creates an 'salida' transaction, an 'entrada' transaction, and a location_transfer record
        within a single database transaction.
        """
        # Validate required fields
        required_fields = ['product_id', 'from_location_id', 'to_location_id', 'quantity', 'user_id']
        for field in required_fields:
            if field not in data or data[field] is None:
                 raise ValueError(f"Missing required field: {field}")

        quantity = data['quantity']
        if quantity <= 0:
             raise ValueError("Transfer quantity must be positive.")

        from_location_id = data['from_location_id']
        to_location_id = data['to_location_id']
        product_id = data['product_id']
        user_id = data['user_id']
        notes = data.get('notes')

        if from_location_id == to_location_id:
             raise ConflictException("Source and destination locations cannot be the same for a transfer.")

        # Check if product, locations, user exist
        product = db.session.get(Product, product_id)
        from_location = db.session.get(Location, from_location_id)
        to_location = db.session.get(Location, to_location_id)
        user = db.session.get(User, user_id) # Assuming User model exists

        if not product:
             raise NotFoundException(f"Product with ID {product_id} not found.")
        if not from_location:
             raise NotFoundException(f"Source Location with ID {from_location_id} not found.")
        if not to_location:
             raise NotFoundException(f"Destination Location with ID {to_location_id} not found.")
        if not user:
             raise NotFoundException(f"User with ID {user_id} not found.")

        # Check if sufficient stock exists at the source location BEFORE creating transactions
        current_stock_at_source = self.transaction_service._get_current_stock(product_id, from_location_id)
        if current_stock_at_source < quantity:
             raise InsufficientStockException(f"Insufficient stock for Product {product_id} at Location {from_location_id}. Available: {current_stock_at_source}, Required: {quantity}.")


        # Use a single database transaction for atomicity
        try:
            # 1. Create the 'salida' transaction
            outgoing_transaction_data = {
                'product_id': product_id,
                'location_id': from_location_id,
                'quantity': -quantity, # Negative quantity for salida
                'transaction_type': TransactionType.salida,
                'user_id': user_id,
                'notes': notes,
                'transaction_date': datetime.utcnow() # Or use a timestamp from data if provided
            }
            outgoing_transaction = InventoryTransaction(**outgoing_transaction_data)
            db.session.add(outgoing_transaction)
            db.session.flush() # Flush to get the transaction_id

            # 2. Create the 'entrada' transaction
            incoming_transaction_data = {
                'product_id': product_id,
                'location_id': to_location_id,
                'quantity': quantity, # Positive quantity for entrada
                'transaction_type': TransactionType.entrada,
                'user_id': user_id,
                'notes': notes,
                 'transaction_date': datetime.utcnow() # Or use a timestamp from data if provided
            }
            incoming_transaction = InventoryTransaction(**incoming_transaction_data)
            db.session.add(incoming_transaction)
            db.session.flush() # Flush to get the transaction_id

            # 3. Link the two transactions using related_transaction_id in inventory_transactions table
            outgoing_transaction.related_transaction = incoming_transaction
            incoming_transaction.related_transaction = outgoing_transaction

            # 4. Create the location_transfer record
            transfer_record_data = {
                'product_id': product_id,
                'from_location_id': from_location_id,
                'to_location_id': to_location_id,
                'quantity': quantity,
                'user_id': user_id,
                'notes': notes,
                'transfer_date': datetime.utcnow() # Or use a timestamp from data if provided
            }
            new_transfer = LocationTransfer(**transfer_record_data)
            db.session.add(new_transfer)

            # Commit the entire transaction
            db.session.commit()

            # The DB trigger trg_update_stock will automatically update stock_levels
            # after these inserts are committed.

            return new_transfer

        except IntegrityError as e:
            db.session.rollback()
            # Log error details
            print(f"Integrity Error during transfer creation: {e}")
            raise ConflictException("Database conflict during transfer creation.")
        except OperationalError as e:
             db.session.rollback()
             print(f"Operational Error during transfer creation: {e}")
             raise DatabaseException(f"Database operational error during transfer: {e}")
        except InsufficientStockException:
             db.session.rollback() # Rollback any partial changes if stock check failed late
             raise # Re-raise the specific exception
        except Exception as e:
            db.session.rollback()
            # Log the error
            print(f"An unexpected error occurred during transfer creation: {e}")
            raise DatabaseException("An unexpected error occurred during transfer creation.")


    # Update/Delete methods for transfers might be restricted.
    # def update_transfer(self, transfer_id, data): ...
    # def delete_transfer(self, transfer_id): ...