# inventory_api/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env and .flaskenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config:
    CORS_ORIGINS = ["http://localhost:3000"]        # qué orígenes permitir (Access-Control-Allow-Origin) :contentReference[oaicite:1]{index=1}
    CORS_METHODS = ["GET","POST","PUT","PATCH","DELETE","OPTIONS"]  # métodos permitidos :contentReference[oaicite:2]{index=2}
    CORS_HEADERS = ["Content-Type","Authorization"]                # headers permitidos :contentReference[oaicite:3]{index=3}
    CORS_AUTOMATIC_OPTIONS = True     # que Flask‑CORS gestione automáticamente las OPTIONS preflight :contentReference[oaicite:4]{index=4}
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # Change this!
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:root@localhost:5432/inventario_db' # Fallback DB URI (replace!)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other general configurations

class DevelopmentConfig(Config):
    DEBUG = True
    # Override development-specific settings if needed

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    # For PostgreSQL, ensure 'TEST_DATABASE_URL' is set or provide a valid direct string:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@host:port/test_db_name'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test-secret-key' # Ensure this is set too
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False # Often disabled for API tests
    # Add any other necessary test-specific configurations
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

class ProductionConfig(Config):
    DEBUG = False
    # Production-specific settings (logging, error handling, etc.)