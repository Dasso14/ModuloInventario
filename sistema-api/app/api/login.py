# inventory_api/app/api/login.py

from flask import request, jsonify
from . import auth_bp # Use the existing auth_bp blueprint
from ..services.login_service import LoginService
# Import ConflictException for registration
from ..utils.exceptions import AuthenticationException, DatabaseException, ApiException, ConflictException, ValueError

login_service = LoginService()

@auth_bp.route('/login', methods=['POST','OPTIONS'])
def login():
    """POST /api/auth/login - Authenticates a user."""
    # --- Manejo explícito de OPTIONS para CORS preflight ---
    if request.method == 'OPTIONS':
        # Flask-CORS debería manejar esto, pero lo añadimos como fallback.
        # Si Flask-CORS está activo y configurado correctamente, esta línea
        # puede que nunca se alcance.
        return jsonify({}), 200
    # --- Fin del manejo de OPTIONS ---

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    identifier = data.get('identifier') # Can be username or email
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'success': False, 'message': 'Username/email and password are required'}), 400

    if not isinstance(identifier, str) or not identifier.strip():
         return jsonify({'success': False, 'message': 'Invalid identifier format'}), 400

    if not isinstance(password, str) or not password.strip():
         return jsonify({'success': False, 'message': 'Invalid password format'}), 400


    try:
        user = login_service.authenticate_user(identifier.strip(), password.strip())

        # Authentication successful
        # You might return user data here, or generate a JWT token
        # For simplicity, we return basic success and user info
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                # Do NOT return password_hash
            }
        }), 200 # Use 200 OK for successful login

    except AuthenticationException as e:
        # Invalid credentials or inactive user
        return jsonify({'success': False, 'message': str(e)}), 401 # 401 Unauthorized
    except ValueError as e: # Handle specific ValueErrors from authentication process
         return jsonify({'success': False, 'message': str(e)}), 400
    except DatabaseException as e:
        # Database errors
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during login: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred during login'}), 500


# --- New Registration Endpoint ---
@auth_bp.route('/register', methods=['POST','OPTIONS'])
def register():
    """POST /api/auth/register - Registers a new user."""
     # --- Manejo explícito de OPTIONS para CORS preflight ---
    if request.method == 'OPTIONS':
        # Flask-CORS debería manejar esto, pero lo añadimos como fallback.
        # Si Flask-CORS está activo y configurado correctamente, esta línea
        # puede que nunca se alcance.
        return jsonify({}), 200
    # --- Fin del manejo de OPTIONS ---

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400

    # Basic input validation (more detailed validation is in the service)
    if 'username' not in data or 'password' not in data:
         return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    if 'email' in data and (not isinstance(data['email'], str) or not data['email'].strip()):
        # Allow email to be optional, but if present, it must be a non-empty string
         if data['email'] is not None: # Allow explicit null
             return jsonify({'success': False, 'message': 'Email must be a non-empty string or null'}), 400

    # Basic password length check at endpoint level
    if not isinstance(data.get('password'), str) or len(data.get('password', '')) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400


    try:
        new_user = login_service.register_user(data)

        # Registration successful
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                # Do NOT return password_hash
            }
        }), 201 # Use 201 Created for successful resource creation

    except (ValueError, TypeError) as e:
        # Validation errors from service or endpoint
        return jsonify({'success': False, 'message': str(e)}), 400 # 400 Bad Request
    except ConflictException as e:
        # Username or email already exists
        return jsonify({'success': False, 'message': str(e)}), 409 # 409 Conflict
    except DatabaseException as e:
        # Database errors
        return jsonify({'success': False, 'message': str(e)}), 500 # 500 Internal Server Error
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during registration: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred during registration'}), 500
