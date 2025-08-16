from fastapi import Depends, HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError
from ..db.database import Database
from ..utils.query_builder import insert_query, get_query

async def add_user_to_db(user: dict, conn: asyncpg.Connection):
    # query = """
    #     INSERT INTO users (first_name, last_name, email, password_hash, phone_number) VALUES ($1, $2, $3, $4, $5) RETURNING *
    # """
    try:
        query = insert_query(user, table="users", returning="(user_id, first_name, last_name, email, profile_picture, phone_number, status)")
        
        res = await conn.fetchrow(query, *user.values())

        return res
    except UniqueViolationError as e:
        raise HTTPException(status_code=400, detail="A user with that email already exists.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")

async def get_user(email:str, conn: asyncpg.Connection):
    # query = """
    #     SELECT * FROM users WHERE email = $1
    # """

    try:

        query = get_query("email", fetch="*", table="users")
        res = await conn.fetchrow(query, email)

        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")