from fastapi import HTTPException
from ..authentication.services import get_password_hash
from ..utils.query_builder import get_query, update_query
import asyncpg


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
    

async def fetch_user_data_db(user_id: int, fetch:str, conn: asyncpg.Connection ):
    try: 
        query = get_query("user_id", fetch=fetch, table="users")
    
        res = await conn.fetchrow(query, user_id) 
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
    
async def fetch_social_links_db(user_id: int, fetch:str, conn: asyncpg.Connection ):
    try: 
        query = get_query("user_id", fetch=fetch, table="social_links")
    
        res = await conn.fetchrow(query, user_id) 
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
    
async def partial_update_user_db(user_id: int, payload:dict, conn: asyncpg.Connection):
    query = update_query("user_id", model=payload, table="users")
    res = await conn.fetchrow(query, *payload.values(), user_id)

    return res

async def partial_update_links_db(user_id: int, payload:dict, conn: asyncpg.Connection):
    query = update_query("user_id", model=payload, table="social_links")
    res = await conn.fetchrow(query, *payload.values(), user_id)

    return res

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
    password_hash = model.get("password_hash")
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
        password_hash = get_password_hash(password_hash)
        user_update.append(f"password_hash = ${idx}")
        user_values.append(password_hash)
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
        RETURNING first_name, last_name, email, phone_number, profile_picture;
        """
    user_values.append(user_id)
    
    user = await conn.fetchrow (query, *user_values)
    return dict(user) if user else None

