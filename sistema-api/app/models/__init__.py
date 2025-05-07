# inventory_api/app/models/__init__.py

from ..db import db
from .product import Product
from .category import Category
from .supplier import Supplier
from .location import Location
from .inventory_transaction import InventoryTransaction
from .location_transfer import LocationTransfer
from .stock_level import StockLevel
from .stock_level import LowStockItem
from .user import User
from .barcode import Barcode

# This file serves as a central point to import all models
# and provides the db instance.