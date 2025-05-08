import pytest
from flask import Flask
from app.api.reports import reports_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

