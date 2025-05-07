# inventory_api/run.py

import os
from dotenv import load_dotenv

# Load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(basedir, '.flaskenv'))

from app import create_app, db
from app.models import (
    User, Product, Category, Supplier, Location,
    InventoryTransaction, LocationTransfer, StockLevel, Barcode, LowStockItem # Import all models for shell context
)

# Get the environment from FLASK_ENV, default to development
config_name = os.environ.get('FLASK_ENV', 'development')

# Mapping environment names to config classes
config_mapping = {
    'development': 'DevelopmentConfig',
    'testing': 'TestingConfig',
    'production': 'ProductionConfig'
}

# Get the configuration class name based on the environment
config_class_name = config_mapping.get(config_name, 'DevelopmentConfig')

# Create the Flask application using the factory function
app = create_app(config_object=f'config.{config_class_name}') # Pass config class name as string

# Optional: Add a shell context for Flask-Shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Category': Category,
        'Supplier': Supplier,
        'Location': Location,
        'InventoryTransaction': InventoryTransaction,
        'LocationTransfer': LocationTransfer,
        'StockLevel': StockLevel,
        'Barcode': Barcode,
        'LowStockItem': LowStockItem
    }

# The 'flask run' command looks for a callable named 'app' or 'application'
# in the file specified by FLASK_APP. Since we use a factory, we need to
# ensure the created 'app' is available in this module's scope.
# The `create_app` factory in `app/__init__.py` should return the Flask app instance.

# To run directly using `python run.py` (less common than `flask run`):
# if __name__ == '__main__':
#     app.run()