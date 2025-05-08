# inventory_api/app/utils/exceptions.py
class NotFoundException(Exception):
    """Exception raised when a resource is not found."""
    pass

class ValueError(Exception):

    pass

class ConflictException(Exception):
    """Exception raised when a request conflicts with the current state of the resource (e.g., duplicate)."""
    pass

class InsufficientStockException(ConflictException):
    """Exception raised for insufficient stock during transactions or transfers."""
    pass

class DatabaseException(Exception):
    """Base exception for database-related errors not covered by others."""
    pass
class InvalidInputException(Exception):
    """Base exception for database-related errors not covered by others."""
    pass
# ... other exceptions like NotFoundException, ConflictException, etc.

class ApiException(Exception):
    """Base class for custom API exceptions."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class NotFoundException(ApiException):
    """Exception raised for resource not found (HTTP 404)."""
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)

class ConflictException(ApiException):
    """Exception raised for resource conflict (e.g., duplicate entry) (HTTP 409)."""
    def __init__(self, message="Resource conflict"):
        super().__init__(message, status_code=409)

class DatabaseException(ApiException):
    """Exception raised for database errors (HTTP 500 or other)."""
    def __init__(self, message="A database error occurred"):
         # Status code might vary, often 500 Internal Server Error
        super().__init__(message, status_code=500)

class InsufficientStockException(ApiException):
     """Exception raised when there is insufficient stock for an operation (HTTP 400 or 409)."""
     def __init__(self, message="Insufficient stock"):
         super().__init__(message, status_code=409) # Or 400 Bad Request depending on context

class AuthenticationException(ApiException):
    """Exception raised for authentication failures (HTTP 401)."""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)