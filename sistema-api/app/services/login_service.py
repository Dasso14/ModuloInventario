# inventory_api/app/services/login_service.py

from werkzeug.security import check_password_hash, generate_password_hash # Import generate_password_hash
from ..models import User
from ..db import db
# Import ConflictException for handling duplicate users
from ..utils.exceptions import AuthenticationException, DatabaseException, ConflictException, ApiException
from datetime import datetime # Needed for timestamps

class LoginService:
    def __init__(self):
        # No need to inherit from BaseService as login is a specific action
        pass

    def authenticate_user(self, identifier, password):
        """
        Authenticates a user based on username or email and password.

        Args:
            identifier (str): The username or email of the user.
            password (str): The plain text password.

        Returns:
            User: The authenticated User object.

        Raises:
            AuthenticationException: If the user is not found or password is incorrect.
            DatabaseException: If a database error occurs during user lookup.
        """
        try:
            # Attempt to find the user by username or email
            user = db.session.query(User).filter(
                (User.username == identifier) | (User.email == identifier)
            ).first()

            if not user:
                raise AuthenticationException("Invalid username or email.")

            if not user.is_active:
                 raise AuthenticationException("User account is inactive.")

            # Check the password hash
            if not check_password_hash(user.password_hash, password):
                raise AuthenticationException("Invalid password.")

            # If authentication is successful, return the user object
            return user

        except AuthenticationException:
            # Re-raise specific authentication errors
            raise
        except Exception as e:
            # Catch any other unexpected errors during database interaction
            db.session.rollback() # Rollback the session in case of error
            print(f"Database error during authentication: {e}")
            raise DatabaseException("An error occurred while trying to authenticate.")


    def register_user(self, data):
        """
        Registers a new user.

        Args:
            data (dict): Dictionary containing user registration data
                         (e.g., {'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'}).

        Returns:
            User: The newly created User object.

        Raises:
            ValueError: If required data is missing or invalid.
            ConflictException: If username or email already exists.
            DatabaseException: If a database error occurs during creation.
        """
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not password:
            raise ValueError("Username and password are required for registration.")

        # Basic validation (more complex validation can be added)
        if not isinstance(username, str) or not username.strip():
             raise ValueError("Username must be a non-empty string.")
        if email and not isinstance(email, str):
             raise ValueError("Email must be a string.")
        if not isinstance(password, str) or len(password) < 6: # Example minimum length
             raise ValueError("Password must be a string of at least 6 characters.")


        try:
            # Check if username or email already exists
            existing_user = db.session.query(User).filter(
                (User.username == username.strip()) | (User.email == email.strip() if email else False)
            ).first()

            if existing_user:
                if existing_user.username == username.strip():
                    raise ConflictException(f"Username '{username.strip()}' is already taken.")
                if email and existing_user.email == email.strip():
                     raise ConflictException(f"Email '{email.strip()}' is already registered.")


            # Hash the password
            password_hash = generate_password_hash(password.strip())

            # Create new user instance
            new_user = User(
                username=username.strip(),
                email=email.strip() if email else None,
                password_hash=password_hash,
                is_active=True, # Or set to False for email verification flow
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Add to session and commit
            db.session.add(new_user)
            db.session.commit()

            return new_user

        except (ValueError, ConflictException) as e:
             # Re-raise specific validation/conflict errors
             db.session.rollback() # Ensure rollback on errors
             raise
        except Exception as e:
            db.session.rollback()
            print(f"Database error during user registration: {e}")
            raise DatabaseException("An error occurred while trying to register the user.")