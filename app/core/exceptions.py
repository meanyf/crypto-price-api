# exceptions.py
class DomainError(Exception):
    status_code = 400


class UserAlreadyExists(DomainError):
    status_code = 409


class InvalidCredentials(DomainError):
    status_code = 401


class ExternalServiceError(DomainError):
    status_code = 502


class ExternalTimeoutError(ExternalServiceError):
    status_code = 504
