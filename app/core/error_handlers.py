from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import asyncpg
import logging

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    # Request validation (e.g., wrong/missing fields)
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.error(f"[VALIDATION ERROR] {exc} | body={await request.body()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Invalid request data",
                "path": str(request.url),
                "method": request.method,
                "detail": str(exc),
            },
        )

    # HTTPException from CRUD/decorator
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"[HTTP ERROR] {exc.detail} | path={request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP error",
                "path": str(request.url),
                "method": request.method,
                "detail": exc.detail,
            },
        )

    # Foreign key errors (if any escaped)
    @app.exception_handler(asyncpg.ForeignKeyViolationError)
    async def fk_violation_handler(request: Request, exc: asyncpg.ForeignKeyViolationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Foreign key constraint violated",
                "path": str(request.url),
                "method": request.method,
                "detail": str(exc).split("\n")[0],
            },
        )

    # Catch-all fallback
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"[UNEXPECTED ERROR] {exc} | path={request.url}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "path": str(request.url),
                "method": request.method,
            },
        )
