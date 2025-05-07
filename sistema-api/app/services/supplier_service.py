# inventory_api/app/services/supplier_service.py

from .base_service import BaseService
from ..models import Supplier
from ..utils.exceptions import NotFoundException, ConflictException

class SupplierService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = Supplier

    def get_all_suppliers(self, filters=None, pagination=None, sorting=None):
        """Gets all suppliers with optional filtering, pagination, and sorting."""
        # Implement filtering logic specific to Supplier fields (e.g., name, email)
        # Using the base helper for now
        return self._query_all(self.model, filters=filters, pagination=pagination, sorting=sorting)

    def get_supplier_by_id(self, supplier_id):
        """Gets a single supplier by its ID."""
        return self._get_by_id(self.model, supplier_id, id_column_name='supplier_id')

    def create_supplier(self, data):
        """Creates a new supplier."""
        # Add specific validation if needed
        return self._create(self.model, data)

    def update_supplier(self, supplier_id, data):
        """Updates an existing supplier."""
        # Add specific validation if needed
        return self._update(self.model, supplier_id, data, id_column_name='supplier_id')

    def delete_supplier(self, supplier_id):
        """Deletes a supplier (physical delete)."""
        # Schema does not have is_active for suppliers, assuming physical delete.
        # BaseService._delete handles IntegrityError if products are linked.
        return self._delete(self.model, supplier_id, id_column_name='supplier_id')