from fastapi import Depends, HTTPException
import asyncpg
from ..db.database import Database

db = Database()

async def add_user_to_db(user: dict, conn: asyncpg.Connection = Depends(db.get_connection)):
    query = """
        INSERT INTO users (name, email, password_hash) VALUES ($1, $2, $3)
    """
    
    res = await conn.execute(query, *user)

    return res