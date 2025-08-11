from .db_instance import db

async def get_db_connection():
    async with db.get_connection() as conn:
        yield conn