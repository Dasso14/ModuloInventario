# inventory_api/app/services/base_service.py

from sqlalchemy.exc import IntegrityError, OperationalError
from ..db import db
from ..utils.exceptions import NotFoundException, ConflictException, DatabaseException, InsufficientStockException

class BaseService:
    """Base class for all service classes providing common database operations."""

    def __init__(self):
        # The db instance is imported directly in services for simplicity
        pass

    def _query_all(self, model, filters=None, pagination=None, sorting=None):
        """Helper to build a query with filters, pagination, and sorting."""
        query = model.query

        # Apply filters (basic example - needs refinement based on filter structure)
        if filters:
            for field, value in filters.items():
                if hasattr(model, field):
                    # Basic equality filter; needs expansion for ranges, likes, joins, etc.
                    query = query.filter(getattr(model, field) == value)
                # Add logic for filtering on related tables if needed (e.g., category_name)

        # Apply sorting
        if sorting:
            for sort_key, sort_order in sorting.items():
                if hasattr(model, sort_key):
                    column = getattr(model, sort_key)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())
                # Add logic for sorting on related tables if needed

        # Apply pagination
        if pagination and 'page' in pagination and 'limit' in pagination:
            page = max(1, int(pagination['page']))
            limit = max(1, int(pagination['limit']))
            offset = (page - 1) * limit
            query = query.limit(limit).offset(offset)

        return query.all() # Or query.paginate() if using Flask-SQLAlchemy-Pagination

    def _get_by_id(self, model, resource_id, id_column_name='id'):
        """Helper to get a resource by its ID, raising NotFoundException if not found."""
        # Use getattr to handle potentially different PK column names like 'product_id'
        item = db.session.get(model, resource_id)
        if item is None:
             # Try fetching using the column name directly if get didn't work (e.g., non-standard PK)
            item = model.query.filter(getattr(model, id_column_name) == resource_id).first()

        if item is None:
            raise NotFoundException(f"{model.__name__} with ID {resource_id} not found")
        return item

    def _create(self, model, data):
        """Helper to create a new resource."""
        try:
            item = model(**data)
            db.session.add(item)
            db.session.commit()
            return item
        except IntegrityError:
            db.session.rollback()
            # More specific error handling might be needed based on which constraint failed
            raise ConflictException(f"Could not create {model.__name__}. Data conflicts with existing record.")
        except OperationalError as e:
             db.session.rollback()
             raise DatabaseException(f"Database operational error during creation: {e}")
        except Exception as e:
            db.session.rollback()
            # Log the error
            print(f"An unexpected error occurred during {model.__name__} creation: {e}")
            raise DatabaseException(f"An unexpected error occurred during {model.__name__} creation.")


    def _update(self, model, resource_id, data, id_column_name='id'):
        """Helper to update an existing resource by ID."""
        try:
            item = self._get_by_id(model, resource_id, id_column_name=id_column_name)
            for field, value in data.items():
                if hasattr(item, field):
                    setattr(item, field, value)
                # Optionally handle setting relationship objects if data contains IDs
                # e.g., if 'category_id' is in data, find the Category object and set item.category
            db.session.commit()
            return item
        except NotFoundException:
            db.session.rollback() # Rollback if _get_by_id failed (though it raises)
            raise # Re-raise NotFoundException
        except IntegrityError:
            db.session.rollback()
            raise ConflictException(f"Could not update {model.__name__} with ID {resource_id}. Data conflicts.")
        except OperationalError as e:
             db.session.rollback()
             raise DatabaseException(f"Database operational error during update: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"An unexpected error occurred during {model.__name__} update: {e}")
            raise DatabaseException(f"An unexpected error occurred during {model.__name__} update.")


    def _delete(self, model, resource_id, id_column_name='id'):
        """Helper to delete a resource by ID (physical delete)."""
        try:
            item = self._get_by_id(model, resource_id, id_column_name=id_column_name)
            db.session.delete(item)
            db.session.commit()
            return True
        except NotFoundException:
            db.session.rollback()
            raise
        except IntegrityError:
            db.session.rollback()
            raise ConflictException(f"Could not delete {model.__name__} with ID {resource_id} due to related records.")
        except OperationalError as e:
             db.session.rollback()
             raise DatabaseException(f"Database operational error during deletion: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"An unexpected error occurred during {model.__name__} deletion: {e}")
            raise DatabaseException(f"An unexpected error occurred during {model.__name__} deletion.")

    def _logical_delete(self, model, resource_id, id_column_name='id'):
        """Helper for logical deletion (sets is_active=False). Assumes model has 'is_active'."""
        try:
            item = self._get_by_id(model, resource_id, id_column_name=id_column_name)
            if not hasattr(item, 'is_active'):
                 raise AttributeError(f"Model {model.__name__} does not have 'is_active' attribute for logical delete.")
            item.is_active = False
            db.session.commit()
            return True
        except NotFoundException:
            db.session.rollback()
            raise
        except OperationalError as e:
             db.session.rollback()
             raise DatabaseException(f"Database operational error during logical delete: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"An unexpected error occurred during {model.__name__} logical delete: {e}")
            raise DatabaseException(f"An unexpected error occurred during {model.__name__} logical delete.")