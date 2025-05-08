# inventory_api/app/services/inventory_service.py

# Import Blueprint along with request and jsonify
# NOTE: Blueprint definition and service instantiation should ideally be in the API routes file (inventory.py)
# and imported/accessed from there. Keeping them here for now as per previous examples,
# but be aware this is not a standard Flask pattern.
from flask import request, jsonify, Blueprint

# Import your backend service layer base class
from ..services.base_service import BaseService

# Import your SQLAlchemy database instance
from ..db import db

# Import your models
from ..models import (
    InventoryTransaction,
    StockLevel,
    LocationTransfer,
    Product, # Needed for validation
    Location, # Needed for validation
    User, # Needed for validation
)

# Import your custom exceptions and the TransactionType enum
from ..utils.exceptions import (
    NotFoundException,
    ConflictException, # Might be needed for unique constraints or logic conflicts
    DatabaseException,
    InsufficientStockException, # Important for removals/transfers
    InvalidInputException # Custom exception for bad data
)
# Corrected import for the TransactionType enum - using uppercase T
from ..utils.enums import TransactionType

from sqlalchemy.exc import IntegrityError # To catch database constraint violations


class InventoryService(BaseService):
    def __init__(self):
        # InventoryService interacts with multiple models, so we don't set a single self.model here
        super().__init__()

    def create_inventory_transaction(self, data):
        """
        Creates a new inventory transaction (add, remove, or adjust)
        and updates the corresponding stock level.

        Args:
            data (dict): A dictionary containing transaction details.
                         Expected keys: product_id, location_id, quantity, user_id,
                                        transaction_type ('entrada', 'salida', 'ajuste',
                                        'transferencia_origen', 'transferencia_destino'),
                                        reference_number (optional), notes (optional).

        Returns:
            InventoryTransaction: The newly created transaction object.

        Raises:
            NotFoundException: If product, location, or user not found.
            InvalidInputException: If data is invalid (e.g., quantity type, transaction_type).
            InsufficientStockException: If removing/adjusting more stock than available.
            DatabaseException: For other database errors.
        """
        # Basic data validation
        required_fields = ['product_id', 'location_id', 'quantity', 'user_id', 'transaction_type']
        if not all(field in data and data[field] is not None for field in required_fields):
             raise InvalidInputException(f"Missing required fields: {', '.join(required_fields)}")

        try:
            product_id = int(data['product_id'])
            location_id = int(data['location_id'])
            user_id = int(data['user_id'])
            # Ensure quantity is a valid number (can be positive or negative)
            try:
                quantity = float(data['quantity'])
            except (ValueError, TypeError):
                 raise InvalidInputException('Invalid quantity value')

            transaction_type_str = data['transaction_type']

            # Validate transaction type string against the enum
            try:
                # Use the imported name: TransactionType
                transaction_type_enum = TransactionType[transaction_type_str]
            except KeyError:
                 raise InvalidInputException(f"Invalid transaction type: {transaction_type_str}. Must be one of {list(TransactionType.__members__.keys())}")

        except (ValueError, TypeError) as e:
            # This block might be redundant due to the specific quantity try/except,
            # but can catch errors if other fields were expected to be int/float.
            raise InvalidInputException(f"Invalid data type for one or more fields: {e}")

        # Check if related entities exist
        product = db.session.get(Product, product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found.")

        location = db.session.get(Location, location_id)
        if not location:
            raise NotFoundException(f"Location with ID {location_id} not found.")

        user = db.session.get(User, user_id)
        if not user:
            # In a real app, user should be from authenticated context, not request body
            raise NotFoundException(f"User with ID {user_id} not found.")

        # --- Stock Level Update Logic ---
        # Find or create the stock level entry for this product and location
        stock_level = db.session.query(StockLevel).filter_by(
            product_id=product_id,
            location_id=location_id
        ).first()

        if not stock_level:
            # If no stock level exists, create one with 0 quantity initially
            stock_level = StockLevel(
                product_id=product_id,
                location_id=location_id,
                quantity=0,
                last_updated=db.func.current_timestamp()
            )
            db.session.add(stock_level)
            # Flush to get the stock_id if needed later, but not strictly necessary here

        # Calculate new quantity based on transaction type
        new_stock_quantity = stock_level.quantity

        # Use the imported name: TransactionType
        if transaction_type_enum == TransactionType.entrada:
            if quantity <= 0:
                 raise InvalidInputException("Quantity must be positive for 'entrada' transaction.")
            new_stock_quantity += quantity
            # For 'add', the transaction quantity is the positive amount added

        # Use the imported name: TransactionType
        elif transaction_type_enum == TransactionType.salida:
             if quantity <= 0:
                 raise InvalidInputException("Quantity must be positive for 'salida' transaction.")
             if stock_level.quantity < quantity:
                 raise InsufficientStockException(
                     f"Insufficient stock for Product ID {product_id} at Location ID {location_id}. "
                     f"Available: {stock_level.quantity}, Attempted Removal: {quantity}"
                 )
             new_stock_quantity -= quantity
             # For 'remove', the transaction quantity is the positive amount removed

        # Use the imported name: TransactionType
        elif transaction_type_enum == TransactionType.ajuste:
            if quantity == 0:
                 raise InvalidInputException("Adjustment quantity cannot be zero.")
            # For 'ajust', the transaction quantity is the signed amount of the adjustment
            new_stock_quantity += quantity
            # Check for negative stock after adjustment
            if new_stock_quantity < 0:
                 # This might indicate an error in the adjustment logic or data
                 # Decide if negative stock is allowed for adjustments or raise error
                 # Raising InsufficientStockException for negative result is reasonable
                 raise InsufficientStockException(
                     f"Adjustment for Product ID {product_id} at Location ID {location_id} "
                     f"would result in negative stock. Current: {stock_level.quantity}, Adjustment: {quantity}"
                 )
        # Add handling for transfer types if create_inventory_transaction is used for them
        # Use the imported name: TransactionType
        elif transaction_type_enum == TransactionType.transferencia_origen:
             if quantity <= 0:
                 raise InvalidInputException("Quantity must be positive for 'transferencia_origen' transaction.")
             if stock_level.quantity < quantity:
                 raise InsufficientStockException(
                     f"Insufficient stock for Product ID {product_id} at Source Location ID {location_id} for transfer. "
                     f"Available: {stock_level.quantity}, Attempted Transfer Out: {quantity}"
                 )
             new_stock_quantity -= quantity
        # Use the imported name: TransactionType
        elif transaction_type_enum == TransactionType.transferencia_destino:
             if quantity <= 0:
                 raise InvalidInputException("Quantity must be positive for 'transferencia_destino' transaction.")
             new_stock_quantity += quantity

        else:
            # This case should be caught by the initial transaction_type validation,
            # but included for safety.
            raise InvalidInputException(f"Unhandled transaction type: {transaction_type_str}")


        # Update the stock level quantity and last updated time
        stock_level.quantity = new_stock_quantity
        stock_level.last_updated = db.func.current_timestamp()

        # --- Create Inventory Transaction ---
        new_transaction = InventoryTransaction(
            transaction_date=db.func.current_timestamp(),
            # Use the imported name: TransactionType
            transaction_type=transaction_type_enum,
            product_id=product_id,
            location_id=location_id,
            # Store the quantity as provided in the transaction data (positive for add/remove, signed for adjust)
            # Use the imported name: TransactionType
            quantity=quantity if transaction_type_enum in [TransactionType.entrada, TransactionType.salida, TransactionType.transferencia_origen, TransactionType.transferencia_destino] else quantity,
            reference_number=data.get('reference_number'),
            notes=data.get('notes'),
            user_id=user_id,
            # related_transaction will be set for transfers, not simple transactions
            related_transaction=data.get('related_transaction'), # Allow setting related_transaction
            created_at=db.func.current_timestamp()
        )

        db.session.add(new_transaction)

        try:
            # Commit the session to save the new transaction and updated stock level
            db.session.commit()
            return new_transaction
        except IntegrityError as e:
            db.session.rollback()
            # Catch specific integrity errors if needed, e.g., FK violations
            raise DatabaseException(f"Database integrity error during transaction: {e}")
        except Exception as e:
            db.session.rollback()
            # Log the error server-side
            print(f"Database error during transaction commit: {e}")
            raise DatabaseException('Database error occurred during transaction commit')


    def create_location_transfer(self, data):
        """
        Creates a new location transfer and the associated inventory transactions.

        Args:
            data (dict): A dictionary containing transfer details.
                         Expected keys: product_id, from_location_id, to_location_id,
                                        quantity, user_id, notes (optional).

        Returns:
            LocationTransfer: The newly created transfer object.

        Raises:
            NotFoundException: If product, locations, or user not found.
            InvalidInputException: If data is invalid (e.g., quantity type, same locations).
            InsufficientStockException: If not enough stock at the source location.
            DatabaseException: For other database errors.
        """
        required_fields = ['product_id', 'from_location_id', 'to_location_id', 'quantity', 'user_id']
        if not all(field in data and data[field] is not None for field in required_fields):
             raise InvalidInputException(f"Missing required fields: {', '.join(required_fields)}")

        try:
            product_id = int(data['product_id'])
            from_location_id = int(data['from_location_id'])
            to_location_id = int(data['to_location_id'])
            user_id = int(data['user_id'])
            # Ensure quantity is a valid number
            try:
                quantity = float(data['quantity'])
            except (ValueError, TypeError):
                 raise InvalidInputException('Invalid quantity value')


        except (ValueError, TypeError) as e:
             # This block might be redundant due to the specific quantity try/except
            raise InvalidInputException(f"Invalid data type for one or more fields: {e}")

        if from_location_id == to_location_id:
             raise InvalidInputException("Source and destination locations cannot be the same.")

        if quantity <= 0:
             raise InvalidInputException("Transfer quantity must be positive.")

        # Check if related entities exist
        product = db.session.get(Product, product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found.")

        from_location = db.session.get(Location, from_location_id)
        if not from_location:
            raise NotFoundException(f"Source Location with ID {from_location_id} not found.")

        to_location = db.session.get(Location, to_location_id)
        if not to_location:
            raise NotFoundException(f"Destination Location with ID {to_location_id} not found.")

        user = db.session.get(User, user_id)
        if not user:
             # In a real app, user should be from authenticated context
            raise NotFoundException(f"User with ID {user_id} not found.")

        # --- Check Stock at Source ---
        source_stock_level = db.session.query(StockLevel).filter_by(
            product_id=product_id,
            location_id=from_location_id
        ).first()

        if not source_stock_level or source_stock_level.quantity < quantity:
             raise InsufficientStockException(
                 f"Insufficient stock for Product ID {product_id} at Source Location ID {from_location_id}. "
                 f"Available: {source_stock_level.quantity if source_stock_level else 0}, Attempted Transfer: {quantity}"
             )

        # --- Create Location Transfer Record ---
        new_transfer = LocationTransfer(
            transfer_date=db.func.current_timestamp(),
            product_id=product_id,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            quantity=quantity,
            notes=data.get('notes'),
            user_id=user_id,
            created_at=db.func.current_timestamp()
        )
        db.session.add(new_transfer)
        # Flush the session to get the transfer_id before creating transactions
        db.session.flush()

        # --- Create Associated Inventory Transactions ---
        # Transaction for removal from source
        # Call create_inventory_transaction for the removal part
        remove_transaction_data = {
            'product_id': product_id,
            'location_id': from_location_id,
            'quantity': quantity, # Positive quantity for removal
            'user_id': user_id,
            'reference_number': f"Transfer Out {new_transfer.transfer_id}", # Link to transfer
            'notes': f"Stock transferred to Location {to_location.name}. {data.get('notes', '')}".strip(),
            'transaction_type': 'transferencia_origen', # Use the specific transfer type
            'related_transaction': None # Will link later if needed
        }
        # Pass the session to create_inventory_transaction so it doesn't commit prematurely
        remove_transaction = self.create_inventory_transaction(remove_transaction_data)


        # Transaction for addition to destination
        # Call create_inventory_transaction for the addition part
        add_transaction_data = {
            'product_id': product_id,
            'location_id': to_location_id,
            'quantity': quantity, # Positive quantity for addition
            'user_id': user_id,
            'reference_number': f"Transfer In {new_transfer.transfer_id}", # Link to transfer
            'notes': f"Stock transferred from Location {from_location.name}. {data.get('notes', '')}".strip(),
            'transaction_type': 'transferencia_destino', # Use the specific transfer type
            'related_transaction': None # Will link later if needed
        }
         # Pass the session to create_inventory_transaction so it doesn't commit prematurely
        add_transaction = self.create_inventory_transaction(add_transaction_data)

        # Optional: Link the two inventory transactions to each other if your schema supports it
        # This requires updating the transaction objects after they are created and added to the session
        # remove_transaction.related_transaction = add_transaction.transaction_id
        # add_transaction.related_transaction = remove_transaction.transaction_id
        # db.session.add_all([remove_transaction, add_transaction]) # Add them if not already added by create_inventory_transaction

        # --- Update Stock Levels ---
        # The create_inventory_transaction calls above already handle stock level updates
        # for their respective locations. We don't need to update stock levels here again.


        try:
            # Commit the entire transaction (transfer record + two inventory transactions)
            db.session.commit()
            return new_transfer
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseException(f"Database integrity error during transfer: {e}")
        except Exception as e:
            db.session.rollback()
            # Log the error server-side
            print(f"Database error during transfer commit: {e}")
            raise DatabaseException('Database error occurred during transfer commit')

    # You might add other methods here for fetching inventory data,
    # like getting stock levels for a product across locations,
    # or fetching transaction/transfer history (though reportService might handle this).

    # Example: Get stock level for a specific product and location
    # def get_stock_level(self, product_id, location_id):
    #     stock = db.session.query(StockLevel).filter_by(
    #         product_id=product_id,
    #         location_id=location_id
    #     ).first()
    #     if not stock:
    #         # Return 0 if no stock entry exists
    #         return StockLevel(product_id=product_id, location_id=location_id, quantity=0)
    #     return stock
