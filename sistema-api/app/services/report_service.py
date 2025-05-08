# inventory_api/app/services/report_service.py

from .base_service import BaseService
# Import models needed for queries
from ..models import (
    StockLevel,
    LowStockItem,
    Product,
    Location,
    InventoryTransaction, # Import InventoryTransaction model
    LocationTransfer, # Import LocationTransfer model
    User # Import User model for joins/filters
)
from ..db import db
from ..utils.exceptions import DatabaseException
from sqlalchemy import func, and_ # For calling DB functions and combining filters
from sqlalchemy.exc import OperationalError
from datetime import datetime, timedelta # Import timedelta for date range filtering


class ReportService(BaseService):
    """
    Service class for generating various inventory reports.
    Handles fetching data for stock levels, low stock, transactions, and transfers.
    Converts SQLAlchemy objects to dictionaries for API response.
    """

    def get_stock_levels(self, filters=None, pagination=None, sorting=None):
        """
        Gets current stock levels for each product/location combination.
        Reads from the 'stock_levels' table (updated by trigger).
        Filters can include: product_id, location_id, category_id, supplier_id.
        Supports pagination and sorting. Returns a list of dictionaries.
        """
        # Start with the base query joining StockLevel with Product and Location
        # Ensure relationships are defined in your models for these joins to work
        query = StockLevel.query.join(Product).join(Location)

        # Apply filters
        if filters:
            if 'product_id' in filters and filters['product_id'] is not None:
                query = query.filter(StockLevel.product_id == filters['product_id'])
            if 'location_id' in filters and filters['location_id'] is not None:
                query = query.filter(StockLevel.location_id == filters['location_id'])
            # Filter via joined Product table (assuming Product model has category_id and supplier_id)
            if 'category_id' in filters and filters['category_id'] is not None:
                 query = query.filter(Product.category_id == filters['category_id'])
            if 'supplier_id' in filters and filters['supplier_id'] is not None:
                 query = query.filter(Product.supplier_id == filters['supplier_id'])
            # Add more filters as needed based on StockLevel, Product, Location fields

        # Apply sorting
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Determine the column to sort by, handling joined fields
                column = None
                if sort_key == 'product_name':
                    column = Product.name # Sort by Product name
                elif sort_key == 'location_name':
                    column = Location.name # Sort by Location name
                elif sort_key == 'quantity':
                    column = StockLevel.quantity # Direct column on StockLevel
                elif sort_key == 'last_updated':
                    column = StockLevel.last_updated # Direct column on StockLevel
                # Add sorting for other relevant fields if needed and available via joins

                if column is not None:
                    if sort_order.lower() == 'desc':
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())

        # Default sorting if no sorting is specified
        if not sorting:
             # Default sort by product name and then location name
             query = query.order_by(Product.name.asc(), Location.name.asc())

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page'])) # Ensure page is at least 1
            limit = max(1, int(pagination['limit'])) # Ensure limit is at least 1
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
        else:
            # If no pagination, return all results
            items = query.all()

        # --- Convert list of SQLAlchemy objects to list of dictionaries ---
        # This assumes your StockLevel model (or related models) have a .to_dict() method
        return [item.to_dict() for item in items]
        # -----------------------------------------------------------------


    def get_low_stock_items(self, filters=None, pagination=None, sorting=None):
        """
        Gets items where current stock is at or below the minimum stock level.
        Reads from the 'low_stock' view (mapped to LowStockItem model).
        Filters can be applied based on view columns (product_id, location_id, etc.).
        Supports pagination and sorting. Returns a list of dictionaries.
        """
        # Query the model mapped to the low_stock view
        query = LowStockItem.query

        # Apply filters (based on view columns available in LowStockItem model)
        if filters:
             if 'product_id' in filters and filters['product_id'] is not None:
                query = query.filter(LowStockItem.product_id == filters['product_id'])
             if 'location_id' in filters and filters['location_id'] is not None:
                query = query.filter(LowStockItem.location_id == filters['location_id'])
            # Add filters for other columns directly available in the low_stock view
            # If you need to filter by category or supplier names, ensure your low_stock view
            # includes those columns or join Product/Location here if relationships are mapped.

        # Apply sorting (based on view columns available in LowStockItem model)
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Handle sorting by view columns
                if hasattr(LowStockItem, sort_key): # Check if the model has the attribute
                    column = getattr(LowStockItem, sort_key)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())
                # Add sorting by related table fields if the view includes them and you mapped relationships

        # Default sorting
        if not sorting:
             # Default sort by product name and then location name in the view
             query = query.order_by(LowStockItem.product_name.asc(), LowStockItem.location_name.asc())

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
        else:
            items = query.all()

        # --- Convert list of SQLAlchemy objects to list of dictionaries ---
        # This assumes your LowStockItem model has a .to_dict() method
        return [item.to_dict() for item in items]
        # -----------------------------------------------------------------


    def get_inventory_total_value(self):
        """
        Calls the database function get_inventory_value() to get the total inventory value.
        Assumes a database function named 'get_inventory_value' exists and returns a scalar value.
        Returns a single numeric value.
        """
        try:
            # Use sqlalchemy.func to call the database function
            # The function is expected to return a single numeric value
            total_value = db.session.query(func.get_inventory_value()).scalar()
            # Return 0.00 if the function returns None (e.g., empty inventory)
            return total_value if total_value is not None else 0.00
        except OperationalError as e:
             # Handle specific database operational errors
             print(f"Operational Error calling get_inventory_value: {e}")
             raise DatabaseException("Could not retrieve total inventory value from the database.")
        except Exception as e:
             # Handle any other unexpected errors
             print(f"An unexpected error occurred calling get_inventory_value: {e}")
             raise DatabaseException("An unexpected error occurred while calculating total inventory value.")


    def get_transaction_history(self, filters=None, pagination=None, sorting=None):
        """
        Gets the history of inventory transactions.
        Filters can include: product_id, location_id, user_id, transaction_type, date range.
        Supports pagination and sorting. Returns a list of dictionaries.
        """
        # Start with the base query for InventoryTransaction
        # Join with Product, Location, and User for filtering and sorting on related fields
        # Ensure relationships are defined in your models for these joins to work
        query = InventoryTransaction.query.join(Product).join(Location).join(User)

        # Apply filters
        if filters:
            if 'product_id' in filters and filters['product_id'] is not None:
                query = query.filter(InventoryTransaction.product_id == filters['product_id'])
            if 'location_id' in filters and filters['location_id'] is not None:
                query = query.filter(InventoryTransaction.location_id == filters['location_id'])
            if 'user_id' in filters and filters['user_id'] is not None:
                query = query.filter(InventoryTransaction.user_id == filters['user_id'])
            if 'transaction_type' in filters and filters['transaction_type'] is not None:
                # Ensure the transaction_type filter matches your TransactionType enum/column type
                query = query.filter(InventoryTransaction.transaction_type == filters['transaction_type'])
            if 'start_date' in filters and filters['start_date'] is not None:
                try:
                    # Parse start date string (assuming format like 'YYYY-MM-DD')
                    start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                    query = query.filter(InventoryTransaction.transaction_date >= start_date)
                except ValueError:
                    # Handle invalid date format if necessary, or assume validation elsewhere
                    print(f"Warning: Invalid start_date format: {filters['start_date']}")
                    pass # Or raise an exception
            if 'end_date' in filters and filters['end_date'] is not None:
                 try:
                    # Parse end date string (assuming format like 'YYYY-MM-DD')
                    # Add one day to include the entire end day for inclusive range
                    end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                    query = query.filter(InventoryTransaction.transaction_date < end_date + timedelta(days=1))
                 except ValueError:
                    print(f"Warning: Invalid end_date format: {filters['end_date']}")
                    pass # Or raise an exception
            # Add filters for other relevant fields (e.g., reference_number)

        # Apply sorting
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Determine the column to sort by, handling joined fields
                column = None
                if sort_key == 'transaction_date':
                    column = InventoryTransaction.transaction_date # Direct column
                elif sort_key == 'product_name':
                    column = Product.name # Via joined Product
                elif sort_key == 'location_name':
                    column = Location.name # Via joined Location
                elif sort_key == 'user_username':
                    column = User.username # Via joined User
                elif sort_key == 'quantity':
                    column = InventoryTransaction.quantity # Direct column
                elif sort_key == 'transaction_type':
                    column = InventoryTransaction.transaction_type # Direct column
                # Add sorting for other relevant fields

                if column is not None:
                    if sort_order.lower() == 'desc':
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())

        # Default sorting if no sorting is specified
        if not sorting:
             # Default sort by transaction date descending
             query = query.order_by(InventoryTransaction.transaction_date.desc())

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
        else:
            # If no pagination, return all results
            items = query.all()

        # --- Convert list of SQLAlchemy objects to list of dictionaries ---
        # This assumes your InventoryTransaction model has a .to_dict() method
        return [item.to_dict() for item in items]
        # -----------------------------------------------------------------


    def get_transfer_history(self, filters=None, pagination=None, sorting=None):
        """
        Gets the history of location transfers.
        Filters can include: product_id, from_location_id, to_location_id, user_id, date range.
        Supports pagination and sorting. Returns a list of dictionaries.
        """
        # Start with the base query for LocationTransfer
        # Join with Product, From Location (aliased), To Location (aliased), and User for filtering/sorting
        # You might need to define aliases for Location in your models for distinct joins
        # Example using aliased Location:
        # from sqlalchemy.orm import aliased
        # FromLocation = aliased(Location)
        # ToLocation = aliased(Location)
        # query = LocationTransfer.query.join(Product).join(
        #     FromLocation, LocationTransfer.from_location_id == FromLocation.location_id
        # ).join(
        #     ToLocation, LocationTransfer.to_location_id == ToLocation.location_id
        # ).join(User)
        # Note: The current join syntax `join(Location, ...)` might work depending on your model definitions,
        # but using aliases is safer for clarity and avoiding potential issues with multiple joins to the same table.
        # For now, keeping the original join syntax as provided, assuming it works with your models.
        query = LocationTransfer.query.join(Product).join(
            Location, LocationTransfer.from_location_id == Location.location_id
        ).join(
            Location, LocationTransfer.to_location_id == Location.location_id
        ).join(User)


        # Apply filters
        if filters:
            if 'product_id' in filters and filters['product_id'] is not None:
                query = query.filter(LocationTransfer.product_id == filters['product_id'])
            if 'from_location_id' in filters and filters['from_location_id'] is not None:
                query = query.filter(LocationTransfer.from_location_id == filters['from_location_id'])
            if 'to_location_id' in filters and filters['to_location_id'] is not None:
                query = query.filter(LocationTransfer.to_location_id == filters['to_location_id'])
            if 'user_id' in filters and filters['user_id'] is not None:
                query = query.filter(LocationTransfer.user_id == filters['user_id'])
            if 'start_date' in filters and filters['start_date'] is not None:
                 try:
                    # Parse start date string (assuming format like 'YYYY-MM-DD')
                    start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                    query = query.filter(LocationTransfer.transfer_date >= start_date)
                 except ValueError:
                    print(f"Warning: Invalid start_date format: {filters['start_date']}")
                    pass # Or raise an exception
            if 'end_date' in filters and filters['end_date'] is not None:
                 try:
                    # Parse end date string (assuming format like 'YYYY-MM-DD')
                    # Add one day to include the entire end day
                    end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                    query = query.filter(LocationTransfer.transfer_date < end_date + timedelta(days=1))
                 except ValueError:
                    print(f"Warning: Invalid end_date format: {filters['end_date']}")
                    pass # Or raise an exception
            # Add filters for other relevant fields (e.g., notes)

        # Apply sorting
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Determine the column to sort by, handling joined fields
                column = None
                if sort_key == 'transfer_date':
                    column = LocationTransfer.transfer_date # Direct column
                elif sort_key == 'product_name':
                    column = Product.name # Via joined Product
                # Sorting by from/to location names requires careful handling with aliased joins
                # If you need this, you'd use something like:
                # elif sort_key == 'from_location_name':
                #     column = FromLocation.name
                # elif sort_key == 'to_location_name':
                #     column = ToLocation.name
                elif sort_key == 'user_username':
                    column = User.username # Via joined User
                elif sort_key == 'quantity':
                    column = LocationTransfer.quantity # Direct column
                # Add sorting for other relevant fields

                if column is not None:
                    if sort_order.lower() == 'desc':
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())

        # Default sorting if no sorting is specified
        if not sorting:
             # Default sort by transfer date descending
             query = query.order_by(LocationTransfer.transfer_date.desc())

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
        else:
            # If no pagination, return all results
            items = query.all()

        # --- Convert list of SQLAlchemy objects to list of dictionaries ---
        # This assumes your LocationTransfer model has a .to_dict() method
        return [item.to_dict() for item in items]
        # -----------------------------------------------------------------

    def get_inventory_total_value(self):
        """
        Calls the database function get_inventory_value() to get the total inventory value.
        Assumes a database function named 'get_inventory_value' exists and returns a scalar value.
        Returns a single numeric value.
        """
        try:
            # Use sqlalchemy.func to call the database function
            # The function is expected to return a single numeric value
            total_value = db.session.query(func.get_inventory_value()).scalar()
            # Return 0.00 if the function returns None (e.g., empty inventory)
            return total_value if total_value is not None else 0.00
        except OperationalError as e:
             # Handle specific database operational errors
             print(f"Operational Error calling get_inventory_value: {e}")
             raise DatabaseException("Could not retrieve total inventory value from the database.")
        except Exception as e:
             # Handle any other unexpected errors
             print(f"An unexpected error occurred calling get_inventory_value: {e}")
             raise DatabaseException("An unexpected error occurred while calculating total inventory value.")

