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
            SELECT user_id, first_name, last_name, email, profile_picture
            FROM users
            WHERE ((first_name || ' ' || last_name) ILIKE '%' || $1 || '%')
            LIMIT 10;
        """

        res = await conn.fetch(query, name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search user on DB -> {e}")

async def get_user_data_db(user_id: int, conn: asyncpg.Connection ):
    try: 
        query = """
        SELECT * FROM users
        WHERE user_id = $1
        """    
    
        res = await conn.fetchrow(query, user_id ) 
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
    
async def update_user_information_db(
    user_id: int,
    model: dict, 
    conn: asyncpg.Connection
):
    
    user_update = []
    user_values = []
    idx = 1
    
    first_name = model.get("first_name")
    last_name = model.get("last_name")
    email = model.get("email")
    phone_number = model.get("phone_number")
    password = model.get("password")
    
    if first_name is not None: 
        user_update.append(f"first_name =  ${idx}")
        user_values.append(first_name)
        idx +=1
        
    if last_name is not None: 
        user_update.append(f"last_name = ${idx}")
        user_values.append(last_name)
        idx +=1
    
    if email is not None: 
        user_update.append(f"email = ${idx}")
        user_values.append(email)
        idx +=1
    
    if password is not None:
        user_update.append(f"password  = ${idx}")
        user_values.append(password)
        idx +=1
        
    if phone_number is not None:
        user_update.append(f"phone_number = ${idx}")
        user_values.append(phone_number)
        idx +=1
        
    if not user_update:
       return None
   
    query = f"""
    
        UPDATE users
            set {", " .join(user_update)} 
        WHERE user_id = ${idx}
        RETURNING *;
        """
    user_values.append(user_id)
    
    user = await conn.fetchrow (query, *user_values)
    return dict(user) if user else None

   

        
    