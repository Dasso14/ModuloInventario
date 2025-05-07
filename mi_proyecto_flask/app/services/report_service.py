# inventory_api/app/services/report_service.py

from .base_service import BaseService
from ..models import StockLevel, LowStockItem, Product, Location, InventoryTransaction
from ..db import db
from ..utils.exceptions import DatabaseException
from sqlalchemy import func # For calling DB functions
from sqlalchemy.exc import OperationalError

class ReportService(BaseService):
    def get_stock_levels(self, filters=None, pagination=None, sorting=None):
        """
        Gets current stock levels for each product/location combination.
        Reads from the 'stock_levels' table (updated by trigger).
        Filters can include: product_id, location_id, category_id, supplier_id.
        """
        query = StockLevel.query.join(Product).join(Location) # Join for filtering/sorting on related names

        # Apply filters
        if filters:
            if 'product_id' in filters:
                query = query.filter(StockLevel.product_id == filters['product_id'])
            if 'location_id' in filters:
                query = query.filter(StockLevel.location_id == filters['location_id'])
            if 'category_id' in filters:
                 query = query.filter(Product.category_id == filters['category_id']) # Filter via joined Product
            if 'supplier_id' in filters:
                 query = query.filter(Product.supplier_id == filters['supplier_id']) # Filter via joined Product
            # Add more filters as needed

        # Apply sorting
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Handle sorting by joined fields
                if sort_key == 'product_name':
                    column = Product.name
                elif sort_key == 'location_name':
                    column = Location.name
                elif sort_key == 'quantity':
                    column = StockLevel.quantity # Direct column
                elif sort_key == 'last_updated':
                    column = StockLevel.last_updated # Direct column
                else:
                    continue # Skip unknown sort keys

                if sort_order.lower() == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

        # Default sorting
        if not sorting:
             query = query.order_by(Product.name, Location.name) # Default sort by product and location name

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
            return items
        else:
            return query.all()


    def get_low_stock_items(self, filters=None, pagination=None, sorting=None):
        """
        Gets items where current stock is at or below the minimum stock level.
        Reads from the 'low_stock' view.
        Filters can be applied based on view columns (product_id, location_id, etc.).
        """
        # Query the model mapped to the low_stock view
        query = LowStockItem.query

        # Apply filters (based on view columns)
        if filters:
             if 'product_id' in filters:
                query = query.filter(LowStockItem.product_id == filters['product_id'])
             if 'location_id' in filters:
                query = query.filter(LowStockItem.location_id == filters['location_id'])
            # Note: Filtering by category/supplier name might require joining Product/Location in the service
            # query or adding those columns/joins to the 'low_stock' view itself.
            # Assuming for now filters are on columns directly available in the view.

        # Apply sorting (based on view columns)
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Handle sorting by view columns
                if hasattr(LowStockItem, sort_key):
                    column = getattr(LowStockItem, sort_key)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())
                # Add sorting by related table fields if the view includes them and you mapped relationships

        # Default sorting
        if not sorting:
             query = query.order_by(LowStockItem.product_name, LowStockItem.location_name)

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
            return items
        else:
            return query.all()

    def get_inventory_total_value(self):
        """
        Calls the database function get_inventory_value() to get the total inventory value.
        """
        try:
            # Use sqlalchemy.func to call the database function
            # The function is expected to return a single numeric value
            total_value = db.session.query(func.get_inventory_value()).scalar()
            return total_value if total_value is not None else 0.00
        except OperationalError as e:
             # Handle database errors during function call
             print(f"Operational Error calling get_inventory_value: {e}")
             raise DatabaseException("Could not retrieve total inventory value from the database.")
        except Exception as e:
             print(f"An unexpected error occurred calling get_inventory_value: {e}")
             raise DatabaseException("An unexpected error occurred while calculating total inventory value.")


    # The endpoints for transaction and transfer history (/api/transactions, /api/transfers)
    # are handled by the TransactionService and TransferService get_all methods.
    # They don't need dedicated methods here unless they require specific report logic
    # not present in the general listing methods.
    # def get_transaction_history(...): # Use TransactionService.get_all_transactions
    # def get_transfer_history(...): # Use TransferService.get_all_transfers