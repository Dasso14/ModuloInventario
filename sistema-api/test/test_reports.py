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

def test_get_stock_levels(client):
    response = client.get('/api/reports/stock-levels')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["product_name"] == "SKU001 - Producto Ejemplo 1"

def test_get_stock_levels_with_params(client):
    response = client.get('/api/reports/stock-levels?productId=1&locationId=2')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Seguimos esperando el mock
    # Aquí no filtramos de verdad, porque es un mock

def test_get_low_stock_report(client):
    response = client.get('/api/reports/low-stock')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[1]["sku"] == "SKU003"

def test_get_low_stock_report_with_params(client):
    response = client.get('/api/reports/low-stock?locationId=1')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
