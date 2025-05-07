# app/api/reports.py
from flask import Blueprint, request, jsonify
# from app.services import report_service
# from app.schemas.stock_level_schema import StockLevelSchema # Asumiendo esquemas
# from app.schemas.low_stock_schema import LowStockSchema
# from marshmallow import ValidationError

reports_bp = Blueprint('reports_bp', __name__) # El prefijo /api/reports se define en app/__init__.py

# stock_level_schema = StockLevelSchema(many=True)
# low_stock_schema = LowStockSchema(many=True)

@reports_bp.route('/stock-levels', methods=['GET']) # Ruta es /api/reports/stock-levels
def get_stock_levels():
    """Obtener el nivel de stock actual para cada combinación producto/ubicación."""
    # Parámetros de consulta opcionales para filtrar
    product_id = request.args.get('productId', None, type=int)
    location_id = request.args.get('locationId', None, type=int)
    category_id = request.args.get('categoryId', None, type=int)
    supplier_id = request.args.get('supplierId', None, type=int)
    # Otros filtros que puedas necesitar (page, limit, sortBy, order)

    # Lógica para llamar al servicio:
    # stock_levels_data = report_service.get_current_stock_levels(
    #     product_id=product_id, location_id=location_id,
    #     category_id=category_id, supplier_id=supplier_id
    # )
    # return jsonify(success=True, data=stock_level_schema.dump(stock_levels_data)), 200

    # Placeholder:
    print(f"Filtros niveles de stock: productId={product_id}, locationId={location_id}, categoryId={category_id}, supplierId={supplier_id}")
    mock_stock_levels = [
        {
            "stock_id": 1, # Este ID vendría de tu tabla/vista current_stock_levels
            "product_id": 1, "product_name": "SKU001 - Producto Ejemplo 1",
            "location_id": 1, "location_name": "Almacén Principal",
            "quantity": 15, "last_updated": "2023-05-07T12:00:00Z"
        },
        {
            "stock_id": 2,
            "product_id": 2, "product_name": "SKU002 - Otro Producto",
            "location_id": 2, "location_name": "Tienda Centro",
            "quantity": 8, "last_updated": "2023-05-03T11:00:00Z"
        }
    ]
    return jsonify(mock_stock_levels), 200

@reports_bp.route('/low-stock', methods=['GET']) # Ruta es /api/reports/low-stock
def get_low_stock_report():
    """Obtener una lista de productos/ubicaciones con stock bajo."""
    # Parámetros de consulta opcionales (similares a stock-levels si es necesario)
    location_id = request.args.get('locationId', None, type=int)
    category_id = request.args.get('categoryId', None, type=int)
    supplier_id = request.args.get('supplierId', None, type=int)

    # Lógica para llamar al servicio:
    # low_stock_data = report_service.get_low_stock_items(
    #     location_id=location_id, category_id=category_id, supplier_id=supplier_id
    # )
    # return jsonify(success=True, data=low_stock_schema.dump(low_stock_data)), 200

    # Placeholder:
    print(f"Filtros reporte stock bajo: locationId={location_id}, categoryId={category_id}, supplierId={supplier_id}")
    mock_low_stock = [
        {
            "product_id": 1, "sku": "SKU001", "product_name": "Producto Ejemplo 1",
            "location_id": 1, "location_name": "Almacén Principal",
            "quantity": 5, # Stock actual
            "min_stock": 10 # Stock mínimo definido para el producto
        },
        {
            "product_id": 3, "sku": "SKU003", "product_name": "Producto Escaso",
            "location_id": 2, "location_name": "Tienda Centro",
            "quantity": 2,
            "min_stock": 5
        }
    ]
    return jsonify(mock_low_stock), 200
