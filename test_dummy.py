# app/task/test_dummy_full.py

import asyncio
import asyncpg
from fastapi import HTTPException
from json import JSONDecodeError
import traceback

from app.task.crud.task_crud import db_error_handler  # your decorator import


@db_error_handler
async def dummy_func(exc_type=None):
    """Raise different exception types based on exc_type parameter."""
    if exc_type:
        # Provide arguments as needed for different exception types
        if exc_type in (asyncpg.UniqueViolationError, asyncpg.ForeignKeyViolationError, asyncpg.PostgresError):
            raise exc_type("test error", None, None)
        elif exc_type == JSONDecodeError:
            raise exc_type("Expecting value", "{}", 0)
        else:
            raise exc_type("test error")
    return "ok"


async def run_tests():
    error_types = [
        None,
        asyncpg.UniqueViolationError,
        asyncpg.ForeignKeyViolationError,
        asyncpg.PostgresError,
        JSONDecodeError,
        ValueError,
        Exception,
    ]

    for etype in error_types:
        try:
            result = await dummy_func(etype)
            print(f"Result for {etype}: {result}")
        except HTTPException as e:
            print(f"Caught HTTPException for {etype}: {e.detail}")
        except Exception as e:
            print(f"Caught unexpected exception for {etype}: {e}")


if __name__ == "__main__":
    asyncio.run(run_tests())
