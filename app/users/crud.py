from fastapi import Depends, HTTPException
import asyncpg
from ..db.database import Database

async def add_user_to_db(user: dict, conn: asyncpg.Connection):
    query = """
        INSERT INTO users (first_name, last_name, email, password_hash, phone_number) VALUES ($1, $2, $3, $4, $5) RETURNING *
    """
    
    res = await conn.fetchrow(query, *user.values())

    return res


async def get_user(email:str, conn: asyncpg.Connection):
    query = """
        SELECT * FROM users WHERE email = $1
    """

    res = await conn.fetchrow(query, email)
    
    return res