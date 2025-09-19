class MediaServiceError(Exception):
    """Base class for known errors in Media Service."""

    def __init__(self, message, code=400):
        super().__init__(message)
        self.message = message
        self.code = code


class BadRequestError(MediaServiceError):
    """Invalid input from client"""
    def __init__(self, message="Bad request"):
        super().__init__(message, code=400)


class NotFoundError(MediaServiceError):
    """Requested resource not found"""
    def __init__(self, message="Not found"):
        super().__init__(message, code=404)


class UnauthorizedError(MediaServiceError):
    """Unauthorized access attempt"""
    def __init__(self, message="Unauthorized"):
        super().__init__(message, code=401)


class InternalServiceError(MediaServiceError):
    """System/internal error"""
    def __init__(self, message="Internal server error"):
        super().__init__(message, code=500)
