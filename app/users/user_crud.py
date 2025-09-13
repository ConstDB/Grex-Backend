from fastapi import Depends, HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError
from ..utils.query_builder import insert_query, get_query, update_query


async def fetch_users_by_name(name: str, conn: asyncpg.Connection):
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
    

async def fetch_user_data_db(user_id: int, conn: asyncpg.Connection ):
    try: 
        query = """
        SELECT first_name, last_name, email, phone_number, password_hash, profile_picture
        FROM users
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
    password_hash = model.get("password")
    profile_picture = model.get("profile_picture")
    
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
  
    if phone_number is not None:
        user_update.append(f"phone_number = ${idx}")
        user_values.append(phone_number)
        idx +=1
        
    if password_hash is not None: 
        user_update.append(f"password = ${idx}")
        user_values.append (password_hash)
        idx +=1
    
    if profile_picture is not None:
        user_update.append(f"profile_picture = ${idx}")
        user_values.append(profile_picture)
        idx +=1
        
    if not user_update:
       return None
   
    query = f"""
    
        UPDATE users
            set {", " .join(user_update)} 
        WHERE user_id = ${idx}
        RETURNING first_name, last_name, email, phone_number, password_hash, profile_picture;
        """
    user_values.append(user_id)
    
    user = await conn.fetchrow (query, *user_values)
    return dict(user) if user else None
