# inventory_api/app/services/product_service.py

from .base_service import BaseService
from ..models import Product, Category, Supplier, StockLevel
from ..db import db
from ..utils.exceptions import NotFoundException, ConflictException
from sqlalchemy.orm import joinedload # Import joinedload

class ProductService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = Product # Set the main model for this service

    def get_all_products(self, filters=None, pagination=None, sorting=None):
        """
        Gets all products with optional filtering, pagination, and sorting.
        Filters can include: name, sku, category_id, supplier_id, is_active, min_stock_threshold (custom filter).
        """
        query = self.model.query

        # Apply filters
        if filters:
            if 'sku' in filters:
                query = query.filter(self.model.sku.ilike(f"%{filters['sku']}%")) # Case-insensitive like
            if 'name' in filters:
                query = query.filter(self.model.name.ilike(f"%{filters['name']}%"))
            if 'category_id' in filters:
                 query = query.filter(self.model.category_id == filters['category_id'])
            if 'supplier_id' in filters:
                 query = query.filter(self.model.supplier_id == filters['supplier_id'])
            if 'is_active' in filters is not None: # Allow explicit True/False/None filtering
                 query = query.filter(self.model.is_active == filters['is_active'])
            # Add more complex filters if needed, e.g., min_stock > value, price ranges

        # Apply sorting (needs refinement for complex sorting)
        if sorting:
             for sort_key, sort_order in sorting.items():
                # Example basic sorting on direct columns
                if hasattr(self.model, sort_key):
                    column = getattr(self.model, sort_key)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())
                # Add sorting by related table fields if required, e.g., category name
                # This would involve joining tables in the query and ordering by joined columns.


        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            # SQLAlchemy-Pagination extension is recommended for proper pagination objects
            # For simplicity, basic offset/limit:
            offset = (page - 1) * limit
            items = query.limit(limit).offset(offset).all()
            # For total count (needed for pagination metadata), you'd need query.count() before limit/offset
            # total_items = query.count()
            # total_pages = (total_items + limit - 1) // limit
            return items # , total_items, total_pages # Return metadata if needed
        else:
            return query.all()

    def get_product_by_id(self, product_id):
        """Gets a single product by its ID."""
        # Use the helper from BaseService
        return self._get_by_id(self.model, product_id, id_column_name='product_id')

    def create_product(self, data):
        """Creates a new product."""
        # Use the helper from BaseService
        # Validate required fields in data before passing? API layer might do this.
        # Ensure related IDs exist if provided (e.g., category_id, supplier_id)
        if 'category_id' in data and data['category_id'] is not None:
            if not db.session.get(Category, data['category_id']):
                 raise NotFoundException(f"Category with ID {data['category_id']} not found.")
        if 'supplier_id' in data and data['supplier_id'] is not None:
            if not db.session.get(Supplier, data['supplier_id']):
                 raise NotFoundException(f"Supplier with ID {data['supplier_id']} not found.")

        return self._create(self.model, data)

    def update_product(self, product_id, data):
        """Updates an existing product."""
         # Ensure related IDs exist if provided
        if 'category_id' in data and data['category_id'] is not None:
            if not db.session.get(Category, data['category_id']):
                 raise NotFoundException(f"Category with ID {data['category_id']} not found.")
        if 'supplier_id' in data and data['supplier_id'] is not None:
            if not db.session.get(Supplier, data['supplier_id']):
                 raise NotFoundException(f"Supplier with ID {data['supplier_id']} not found.")

        # Use the helper from BaseService
        return self._update(self.model, product_id, data, id_column_name='product_id')

    def delete_product(self, product_id):
        """Deletes a product (logical delete)."""
        # Use the logical delete helper from BaseService
        return self._logical_delete(self.model, product_id, id_column_name='product_id')

    # Example of a custom service method not directly mapping to CRUD
    def get_products_by_category(self, category_id):
        """Gets all active products in a specific category."""
        return self.model.query.filter(self.model.category_id == category_id, self.model.is_active == True).all()
    
 # --- METHOD TO GET STOCK LEVELS BY PRODUCT ID (FIXED QUERY) ---
    def get_stock_levels_by_product_id(self, product_id):
        """
        Gets all stock levels for a specific product across all locations.
        Returns a list of StockLevel objects with product and location relationships loaded.
        """
        # First, check if the product exists
        # Use the standard model.query or db.session.query
        # Using Product.query is the most idiomatic Flask-SQLAlchemy way
        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found.")

        # Query StockLevel model, filtering by product_id
        # Use StockLevel.query and joinedload
        stock_levels = StockLevel.query\
            .filter(StockLevel.product_id == product_id)\
            .options(joinedload(StockLevel.product), joinedload(StockLevel.location))\
            .all()

        # stock_levels will be a list of StockLevel objects with relationships loaded.
        # The API endpoint will convert these to dictionaries using sl.to_dict().
        return stock_levels
    # --- END METHOD ---