# errors.py

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import DomainError


def register_exception_handlers(app):
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(status_code=exc.status_code, content={"error": str(exc)})
