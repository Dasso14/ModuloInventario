# inventory_api/app/services/__init__.py

from .base_service import BaseService
from .product_service import ProductService
from .category_service import CategoryService
from .supplier_service import SupplierService
from .location_service import LocationService
from .transaction_service import TransactionService
from .transfer_service import TransferService
from .report_service import ReportService
from .inventory_service import InventoryService
from .login_service import LoginService

# Expose services for easy import
__all__ = [
    'InventoryService',
    'BaseService',
    'ProductService',
    'CategoryService',
    'SupplierService',
    'LocationService',
    'TransactionService',
    'TransferService',
    'ReportService',
    'LoginService'
]