# exceptions.py
class DomainError(Exception):
    status_code = 400

    def __init__(self, message: str = None, status_code: int = None):
        self.message = message or self.default_message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class UserAlreadyExists(DomainError):
    status_code = 409
    default_message = "User already exists"


class InvalidCredentials(DomainError):
    status_code = 401
    default_message = "Invalid credentials"


class ExternalAPIError(DomainError):
    default_message = "External API error"

    def __init__(self, message: str = None, status_code: int = None):
        super().__init__(message, status_code)


class ExternalServiceError(ExternalAPIError):
    status_code = 502
    default_message = "External service error"


class ExternalTimeoutError(ExternalAPIError):
    status_code = 504
    default_message = "External timeout error"
