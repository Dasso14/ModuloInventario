# inventory_api/app/api/__init__.py

from flask import Blueprint

# Create Blueprints for each API section
products_bp = Blueprint('products_api', __name__, url_prefix='/api/products')
categories_bp = Blueprint('categories_api', __name__, url_prefix='/api/categories')
suppliers_bp = Blueprint('suppliers_api', __name__, url_prefix='/api/suppliers')
locations_bp = Blueprint('locations_api', __name__, url_prefix='/api/locations')
transactions_bp = Blueprint('transactions_api', __name__, url_prefix='/api/transactions')
transfers_bp = Blueprint('transfers_api', __name__, url_prefix='/api/transfers')
reports_bp = Blueprint('reports_api', __name__, url_prefix='/api/reports') # Blueprint for reports group
inventory_bp = Blueprint('inventory_api', __name__, url_prefix='/api/inventory') # <-- Add this line

# Import routes to associate them with the blueprints
# The files below will define the routes and use these blueprint objects
from . import products
from . import categories
from . import suppliers
from . import locations
from . import transactions # Handles /api/transactions and /api/stock-levels
from . import transfers # Handles /api/transfers list/get
from . import reports    # Handles /api/reports/low-stock, potentially others
from . import inventory

# This file will be imported in your Flask app factory (app/__init__.py)
# to register the blueprints with the Flask application.