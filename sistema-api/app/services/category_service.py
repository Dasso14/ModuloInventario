# inventory_api/app/services/category_service.py

from .base_service import BaseService
from ..models import Category
from ..db import db
from ..utils.exceptions import NotFoundException, ConflictException

class CategoryService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = Category

    def get_all_categories(self, filters=None, pagination=None, sorting=None):
        """Gets all categories with optional filtering, pagination, and sorting."""
        query = self.model.query

        if filters:
             if 'name' in filters:
                query = query.filter(self.model.name.ilike(f"%{filters['name']}%"))
             if 'parent_id' in filters is not None: # Allow filtering for root categories (parent_id is None)
                  query = query.filter(self.model.parent_id == filters['parent_id'])

        # Apply sorting and pagination using helpers
        return self._query_all(self.model, filters=filters, pagination=pagination, sorting=sorting)


    def get_category_by_id(self, category_id):
        """Gets a single category by its ID."""
        return self._get_by_id(self.model, category_id, id_column_name='category_id')

    def create_category(self, data):
        """Creates a new category."""
         # Ensure parent category exists if parent_id is provided
        if 'parent_id' in data and data['parent_id'] is not None:
            if not db.session.get(Category, data['parent_id']):
                 raise NotFoundException(f"Parent Category with ID {data['parent_id']} not found.")

        return self._create(self.model, data)

    def update_category(self, category_id, data):
        """Updates an existing category."""
        # Prevent category from being its own parent
        if 'parent_id' in data and data['parent_id'] == category_id:
             raise ConflictException("A category cannot be its own parent.")

         # Ensure new parent category exists if parent_id is provided
        if 'parent_id' in data and data['parent_id'] is not None:
            if not db.session.get(Category, data['parent_id']):
                 raise NotFoundException(f"Parent Category with ID {data['parent_id']} not found.")
            # Optional: Add logic to prevent creating cycles in the hierarchy

        return self._update(self.model, category_id, data, id_column_name='category_id')

    def delete_category(self, category_id):
        """Deletes a category (physical delete)."""
        # Schema does not have is_active for categories, assuming physical delete.
        # The DB schema has ON DELETE RESTRICT/NO ACTION by default for FKs,
        # so deleting a category with associated products or child categories will raise IntegrityError.
        # The BaseService._delete helper handles the IntegrityError.
        return self._delete(self.model, category_id, id_column_name='category_id')