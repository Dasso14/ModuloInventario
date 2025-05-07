# inventory_api/app/utils/exceptions.py
class NotFoundException(Exception):
    """Exception raised when a resource is not found."""
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