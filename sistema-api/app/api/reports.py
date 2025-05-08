# app/api/reports.py
from flask import Blueprint, request, jsonify
# Import your backend service layers for reports
from ..services.report_service import ReportService
# Removed imports for Marshmallow schemas

from ..utils.exceptions import (
    NotFoundException, # Aunque ya no se usa NotFoundException en estas rutas
    DatabaseException,
    # Import other relevant exceptions from your utils
)

# Define the blueprint for report routes
# The url_prefix='/api/reports' should be registered in app/__init__.py
reports_bp = Blueprint('reports_bp', __name__, url_prefix='/api/reports')

# IMPORTANT: CORS should typically be applied where the blueprint is registered,
# NOT directly within the blueprint file itself.
# In your main application file (e.g., app/__init__.py), you should do:
#
# from flask_cors import CORS
# from .api.reports import reports_bp
#
# # ... your Flask app initialization ...
#
# # Apply CORS to the reports blueprint
# CORS(reports_bp)
#
# # ... register the blueprint ...
# app.register_blueprint(reports_bp)
#
# Or apply CORS to your entire app instance:
# CORS(app)


# Instantiate your service class
report_service = ReportService()
# Removed instantiation for Marshmallow schemas


# --- Rutas Simplificadas (sin lógica de filtros, paginación, ordenamiento) ---

@reports_bp.route('/stock-levels', methods=['GET', 'OPTIONS'])
def get_stock_levels():
    """
    GET /api/reports/stock-levels
    Obtener el nivel de stock actual para cada combinación producto/ubicación.
    """
    # Flask-CORS handles the preflight response. This block is often redundant
    # if CORS is configured correctly, but kept for clarity/fallback.
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Llama al ReportService para obtener todos los niveles de stock
        # (asumiendo que el servicio devuelve datos sin necesidad de parámetros)
        stock_levels_data = report_service.get_stock_levels()

        # Retorna la respuesta de éxito
        return jsonify({'success': True, 'data': stock_levels_data}), 200

    except DatabaseException as e:
        print(f"Database error fetching stock levels: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred while fetching stock levels.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred fetching stock levels: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred while fetching stock levels.'}), 500


@reports_bp.route('/low-stock', methods=['GET', 'OPTIONS'])
def get_low_stock_report():
    """
    GET /api/reports/low-stock
    Obtener una lista de productos/ubicaciones con stock bajo.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Llama al ReportService para obtener el reporte de stock bajo
        low_stock_data = report_service.get_low_stock_items()

        # Retorna la respuesta de éxito
        return jsonify({'success': True, 'data': low_stock_data}), 200

    except DatabaseException as e:
        print(f"Database error fetching low stock report: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred while fetching low stock report.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred fetching low stock report: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred while fetching low stock report.'}), 500


@reports_bp.route('/transactions', methods=['GET', 'OPTIONS'])
def get_transaction_history():
    """
    GET /api/reports/transactions
    Obtener el historial de transacciones de inventario.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Llama al ReportService para obtener el historial de transacciones
        transactions_data = report_service.get_transaction_history()

        # Retorna la respuesta de éxito
        return jsonify({'success': True, 'data': transactions_data}), 200

    except DatabaseException as e:
        print(f"Database error fetching transaction history: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred while fetching transaction history.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred fetching transaction history: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred while fetching transaction history.'}), 500


@reports_bp.route('/transfers', methods=['GET', 'OPTIONS'])
def get_transfer_history():
    """
    GET /api/reports/transfers
    Obtener el historial de transferencias de stock entre ubicaciones.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Llama al ReportService para obtener el historial de transferencias
        transfers_data = report_service.get_transfer_history()

        # Retorna la respuesta de éxito
        return jsonify({'success': True, 'data': transfers_data}), 200

    except DatabaseException as e:
        print(f"Database error fetching transfer history: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred while fetching transfer history.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred fetching transfer history: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred while fetching transfer history.'}), 500

# La ruta get_total_inventory_value ya estaba simplificada, solo llama al servicio
@reports_bp.route('/total-value', methods=['GET', 'OPTIONS'])
def get_total_inventory_value():
    """
    GET /api/reports/total-value
    Obtener el valor total del inventario.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Asumiendo que report_service.get_inventory_total_value devuelve un valor escalar
        total_value = report_service.get_inventory_total_value()
        # Retorna el valor escalar envuelto en un diccionario
        return jsonify({'success': True, 'data': {'total_value': total_value}}), 200
    except DatabaseException as e:
        print(f"Database error fetching total inventory value: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred fetching total inventory value: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500