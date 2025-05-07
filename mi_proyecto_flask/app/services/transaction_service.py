# inventory_api/app/services/transaction_service.py

from .base_service import BaseService
from ..models import InventoryTransaction, Product, Location, User
from ..utils.enums import TransactionType
from ..db import db
from ..utils.exceptions import NotFoundException, ConflictException, InsufficientStockException
from sqlalchemy import desc, asc

class TransactionService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = InventoryTransaction

    def get_all_transactions(self, filters=None, pagination=None, sorting=None):
        """
        Gets all inventory transactions with optional filtering, pagination, and sorting.
        Filters can include: product_id, location_id, user_id, transaction_type,
        start_date, end_date.
        """
        query = self.model.query.join(Product).join(Location).outerjoin(User) # Join for filtering/sorting on names

        # Apply filters
        if filters:
            if 'product_id' in filters:
                 query = query.filter(self.model.product_id == filters['product_id'])
            if 'location_id' in filters:
                 query = query.filter(self.model.location_id == filters['location_id'])
            if 'user_id' in filters:
                 query = query.filter(self.model.user_id == filters['user_id'])
            if 'transaction_type' in filters:
                 # Ensure the filter value is a valid TransactionType enum member
                 try:
                     transaction_type_enum = TransactionType(filters['transaction_type'])
                     query = query.filter(self.model.transaction_type == transaction_type_enum)
                 except ValueError:
                     # Handle invalid transaction type filter value
                     pass # Or raise an error indicating bad request parameter
            if 'start_date' in filters:
                # Assuming start_date is a datetime object or can be parsed
                query = query.filter(self.model.transaction_date >= filters['start_date'])
            if 'end_date' in filters:
                 # Assuming end_date is a datetime object or can be parsed
                 query = query.filter(self.model.transaction_date <= filters['end_date'])
            # Add more filters as needed

        # Apply sorting
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Handle sorting by joined fields (e.g., product_name, location_name, user_name)
                if sort_key == 'product_name':
                    column = Product.name
                elif sort_key == 'location_name':
                    column = Location.name
                elif sort_key == 'user_name':
                    column = User.username
                elif hasattr(self.model, sort_key): # Sorting on direct transaction fields
                    column = getattr(self.model, sort_key)
                else:
                    continue # Skip unknown sort keys

                if sort_order.lower() == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

        # Default sorting if none provided
        if not sorting:
             query = query.order_by(desc(self.model.transaction_date))


        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
            return items # Return list of InventoryTransaction objects
        else:
            return query.all()


    def get_transaction_by_id(self, transaction_id):
        """Gets a single transaction by its ID."""
        # Use join to eager load related data for the response, if desired
        transaction = self.model.query.options(
            db.joinedload(InventoryTransaction.product),
            db.joinedload(InventoryTransaction.location),
            db.joinedload(InventoryTransaction.user)
        ).filter(self.model.id == transaction_id).first()

        if transaction is None:
             raise NotFoundException(f"InventoryTransaction with ID {transaction_id} not found.")
        return transaction


    def create_transaction(self, data):
        """
        Registers a new inventory transaction.
        NOTE: Stock level updates are handled by the database trigger.
        This method only inserts the transaction record.
        """
        # Validate required fields and check if related entities exist
        required_fields = ['product_id', 'location_id', 'quantity', 'transaction_type', 'user_id']
        for field in required_fields:
            if field not in data or data[field] is None:
                 raise ValueError(f"Missing required field: {field}")

        # Validate transaction type string maps to Enum
        try:
            data['transaction_type'] = TransactionType(data['transaction_type'])
        except ValueError:
            raise ValueError(f"Invalid transaction_type: {data['transaction_type']}")

        # Check if product, location, user exist
        if not db.session.get(Product, data['product_id']):
             raise NotFoundException(f"Product with ID {data['product_id']} not found.")
        if not db.session.get(Location, data['location_id']):
             raise NotFoundException(f"Location with ID {data['location_id']} not found.")
        # Assuming User model exists and is used
        if not db.session.get(User, data['user_id']):
             raise NotFoundException(f"User with ID {data['user_id']} not found.")

        # If it's an 'salida' or 'ajuste' with negative quantity, check stock BEFORE inserting
        # NOTE: The DB trigger handles the *actual* stock update based on quantity sign.
        # However, checking *before* insertion gives a faster feedback to the user.
        # This check might be redundant if the DB procedure handles insufficient stock elegantly,
        # but checking here is safer for the API layer.
        if data['transaction_type'] in [TransactionType.salida] or \
           (data['transaction_type'] == TransactionType.ajuste and data['quantity'] < 0):
            current_stock = self._get_current_stock(data['product_id'], data['location_id'])
            required_quantity = data['quantity'] if data['quantity'] > 0 else -data['quantity'] # Always check against positive quantity
            if current_stock is None or current_stock < required_quantity:
                 raise InsufficientStockException(f"Insufficient stock for Product {data['product_id']} at Location {data['location_id']}. Available: {current_stock}, Required: {required_quantity}.")


        # Use the create helper
        # Remove keys from data that are not columns if necessary (e.g., user_name from API input)
        transaction_data = {k: v for k, v in data.items() if hasattr(self.model, k)}
        new_transaction = self._create(self.model, transaction_data)

        # The DB trigger will automatically update stock_levels AFTER the commit.
        # If you needed to access the *new* stock level immediately after this function call,
        # you might need to re-query the stock_levels table or the database function.

        return new_transaction

    # Helper method to get current stock level (useful for checks)
    def _get_current_stock(self, product_id, location_id):
        """Helper to get the current stock quantity for a product at a location."""
        from ..models import StockLevel # Import here to avoid circular dependency if StockLevel imports this service
        stock_item = StockLevel.query.filter_by(product_id=product_id, location_id=location_id).first()
        return stock_item.quantity if stock_item else 0 # Return 0 if no stock record exists

    # Update/Delete methods for transactions might be restricted in a real system
    # as they represent historical events. If needed, they'd be implemented carefully.
    # def update_transaction(self, transaction_id, data): ...
    # def delete_transaction(self, transaction_id): ...