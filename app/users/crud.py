from fastapi import Depends, HTTPException
import asyncpg
from ..db.database import Database

async def add_user_to_db(user: dict, conn: asyncpg.Connection):
    query = """
        INSERT INTO users (name, email, password_hash) VALUES ($1, $2, $3)
    """
    
    res = await conn.fetchval(query, *user.values())

    return res