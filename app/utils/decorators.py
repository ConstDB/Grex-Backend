import functools
import logging
from fastapi import HTTPException
import asyncpg
from json import JSONDecodeError

logger = logging.getLogger(__name__)

def db_error_handler(func):
    """Decorator to catch asyncpg, JSON, Value, and generic errors, re-raise as HTTPExceptions."""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        # Handle all asyncpg errors
        except asyncpg.PostgresError as e:
            error_type = type(e).__name__
            table = getattr(e, "table_name", None)
            constraint = getattr(e, "constraint_name", None)

            # Log concise message
            logger.warning(f"[DB ERROR] {error_type} in {func.__name__} | table={table} | constraint={constraint} | args={args} kwargs={kwargs}")

            # Map specific errors to HTTP status and messages
            if isinstance(e, asyncpg.ForeignKeyViolationError):
                detail = "Foreign key constraint violated"
                status_code = 400
            elif isinstance(e, asyncpg.UniqueViolationError):
                detail = "Unique constraint violated"
                status_code = 400
            else:
                detail = "Database error"
                status_code = 500

            raise HTTPException(
                status_code=status_code,
                detail={
                    "error": detail,
                    "function": func.__name__,
                    "table": table,
                    "constraint": constraint,
                },
            )

        # Re-raise HTTPExceptions untouched
        except HTTPException:
            raise

        # JSON decode errors
        except JSONDecodeError as e:
            logger.warning(f"[JSON ERROR] {func.__name__} | args={args} kwargs={kwargs} | {e}")
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid JSON payload", "function": func.__name__},
            )

        # Value errors from business logic
        except ValueError as e:
            logger.warning(f"[VALUE ERROR] {func.__name__} | args={args} kwargs={kwargs} | {e}")
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid data", "function": func.__name__},
            )

        # Catch-all for unexpected errors
        except Exception as e:
            logger.exception(f"[UNEXPECTED ERROR] {func.__name__} | args={args} kwargs={kwargs}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Internal server error", "function": func.__name__},
            )

    return wrapper
