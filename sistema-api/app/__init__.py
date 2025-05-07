# inventory_api/app/__init__.py

from flask import Flask
from .db import db # Import the db instance
from .api import ( # Import blueprints
    products_bp, categories_bp, suppliers_bp, locations_bp,
    transactions_bp, transfers_bp, reports_bp
)
# Import Flask-Migrate, Flask-Login, etc. if you use them
from flask_migrate import Migrate
# from flask_login import LoginManager # If using Flask-Login

# db = SQLAlchemy() # Don't initialize here, import from app.db
migrate = Migrate()
# login_manager = LoginManager() # If using Flask-Login
# login_manager.login_view = 'auth.login' # Set login route if using Flask-Login


def create_app(config_object='config.DevelopmentConfig'):
    app = Flask(__name__)

    # Load configuration from the specified config class
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # login_manager.init_app(app) # If using Flask-Login

    # Optional: Configure login_manager user loader if using Flask-Login
    # from app.models import User
    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(reports_bp)

    # Register error handlers (if you create them in app/utils/error_handlers.py)
    # from .utils.error_handlers import register_error_handlers
    # register_error_handlers(app)

    return app