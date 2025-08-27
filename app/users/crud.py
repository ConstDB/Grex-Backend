from fastapi import Depends, HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError
from ..utils.query_builder import insert_query, get_query, update_query
from ..utils.logger import logger

async def add_user_to_db(user: dict, conn: asyncpg.Connection):
    # query = """
    #     INSERT INTO users (first_name, last_name, email, password_hash, phone_number) VALUES ($1, $2, $3, $4, $5) RETURNING *
    # """
    try:
        query = insert_query(user, table="users", returning="user_id, first_name, last_name, email, profile_picture, phone_number, status")
        
        res = await conn.fetchrow(query, *user.values())

        return res
    except UniqueViolationError as e:
        raise HTTPException(status_code=400, detail="A user with that email already exists.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")

async def get_user_from_db(email:str, conn: asyncpg.Connection, fetch:str="*"):
    # query = """
    #     SELECT * FROM users WHERE email = $1
    # """

    try:

        query = get_query("email", fetch=fetch, table="users")
        res = await conn.fetchrow(query, email)

        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")

async def update_refresh_token_on_db(user_id:int, payload:dict, conn: asyncpg.Connection):
    try: 
        query = update_query("user_id", model=payload, table="users")
        return await conn.execute(query, *payload.values(), user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")

async def revoke_user_token_on_db(user_id:int, payload:dict, conn: asyncpg.Connection):
    try:
        query = update_query("user_id", model=payload, table="users")
        logger.info(query)
        await conn.execute(query, *payload.values(), user_id)
        return {"message": "Successful Logout"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong on CRUD -> {e}")

async def get_users_by_name(name: str, conn: asyncpg.Connection):
    try:
        query = """
            SELECT first_name, last_name, email, profile_picture
            FROM users
            WHERE first_name ILIKE '%' || $1 || '%'
                OR last_name ILIKE '%' || $1 || '%'
            LIMIT 10;
        """

        res = await conn.fetch(query, name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search user on DB -> {e}")