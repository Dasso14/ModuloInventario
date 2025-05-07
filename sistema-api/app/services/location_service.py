# inventory_api/app/services/location_service.py

from .base_service import BaseService
from ..models import Location
from ..db import db
from ..utils.exceptions import NotFoundException, ConflictException

class LocationService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = Location

    def get_all_locations(self, filters=None, pagination=None, sorting=None):
        """Gets all locations with optional filtering, pagination, and sorting."""
        query = self.model.query

        if filters:
            if 'name' in filters:
                 query = query.filter(self.model.name.ilike(f"%{filters['name']}%"))
            if 'is_active' in filters is not None:
                 query = query.filter(self.model.is_active == filters['is_active'])
            if 'parent_id' in filters is not None: # Maps to parent_location in DB
                 query = query.filter(self.model.parent_id == filters['parent_id'])


        # Apply sorting and pagination using helpers
        return self._query_all(self.model, filters=filters, pagination=pagination, sorting=sorting)


    def get_location_by_id(self, location_id):
        """Gets a single location by its ID."""
        return self._get_by_id(self.model, location_id, id_column_name='location_id')

    def create_location(self, data):
        """Creates a new location."""
        # Ensure parent location exists if parent_id (parent_location) is provided
        if 'parent_id' in data and data['parent_id'] is not None:
            if not db.session.get(Location, data['parent_id']):
                 raise NotFoundException(f"Parent Location with ID {data['parent_id']} not found.")

        return self._create(self.model, data)

    def update_location(self, location_id, data):
        """Updates an existing location."""
         # Prevent location from being its own parent
        if 'parent_id' in data and data['parent_id'] == location_id:
             raise ConflictException("A location cannot be its own parent.")

        # Ensure new parent location exists if parent_id is provided
        if 'parent_id' in data and data['parent_id'] is not None:
            if not db.session.get(Location, data['parent_id']):
                 raise NotFoundException(f"Parent Location with ID {data['parent_id']} not found.")
            # Optional: Add logic to prevent creating cycles

        return self._update(self.model, location_id, data, id_column_name='location_id')

    def delete_location(self, location_id):
        """Deletes a location (logical delete)."""
        # Schema has is_active for locations, so perform logical delete.
        return self._logical_delete(self.model, location_id, id_column_name='location_id')