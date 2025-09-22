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
        query = insert_query(user, table="users", returning="user_id, first_name, last_name, email, profile_picture, phone_number")
        
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


async def insert_social_links_db(payload:dict, conn: asyncpg.Connection):
    query = insert_query(payload, "social_links")

    res = await conn.fetchrow(query, *payload.values())

    return res

        
    