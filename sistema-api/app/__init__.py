from flask import Flask
from flask_cors import CORS
from .db import db
from .api import products_bp, categories_bp, suppliers_bp, locations_bp, transactions_bp, transfers_bp, reports_bp
from flask_migrate import Migrate

migrate = Migrate()

def create_app(config_object='config.DevelopmentConfig'):
    app = Flask(__name__)


    # 2) Config y extensiones
    app.config.from_object(config_object)

    CORS(app)   

    db.init_app(app)
    migrate.init_app(app, db)

    # 3) Registro de blueprints
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(reports_bp)


    return app
