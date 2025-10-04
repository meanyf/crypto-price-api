# exceptions.py
class DomainError(Exception):
    status_code = 400


class UserAlreadyExists(DomainError):
    status_code = 409


class InvalidCredentials(DomainError):
    status_code = 401


