from .crud import fetch_user_data_db, fetch_social_links_db, partial_update_user_db, partial_update_links_db, fetch_user_tasks_db
from .schemas import GetLinksResponse, GetUserResponse
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..authentication.services import verify_hash, get_hash, create_access_token, create_refresh_token
import asyncpg

async def get_user_data_service(user_id: int, conn: asyncpg.Connection):
    user_data_to_fetch = ", ".join(GetUserResponse.model_fields.keys())
    link_data_to_fetch = ", ".join(GetLinksResponse.model_fields.keys())

    user_data = await fetch_user_data_db(user_id, user_data_to_fetch, conn)
    links_data = await fetch_social_links_db(user_id, link_data_to_fetch, conn)

    data = dict(user_data)

    if data["skills"] == None:
        data["skills"] = []
    data["social_links"] = dict(links_data)

    return data


async def partial_update_user_service(user_id: int, payload: dict, conn: asyncpg.Connection):

    filtered_user_payload = {
        key:value for key,value in payload.items() if value != None
    }

    old_data =  await get_user_data_service(user_id, conn)

    if "social_links" in filtered_user_payload:
        links_data = filtered_user_payload.pop("social_links")

        filtered_link_payload = {
            key:value for key,value in links_data.items() if value != None
        }

        await partial_update_links_db(user_id, filtered_link_payload, conn)

    if filtered_user_payload:
        await partial_update_user_db(user_id, filtered_user_payload, conn)
    
    
    new_data = await get_user_data_service(user_id, conn)
    
    if new_data == old_data:
        return {"message": "No changes happened."}
    
    return new_data


async def get_user_tasks_services(user_id:int, conn:asyncpg.Connection):
    return await fetch_user_tasks_db(user_id, conn)

async def change_password_service(user_id: int, payload: dict, conn:asyncpg.Connection):
    user = await fetch_user_data_db(user_id, fetch="email, password_hash", conn=conn)
    user = dict(user)
    current_password = user["password_hash"]
    old_password = payload["old_password"]
    new_password = payload["new_password"]

    if not verify_hash(plain_text=old_password, hashed_text=current_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    if verify_hash(plain_text=new_password, hashed_text=current_password):
        raise HTTPException(status_code=400, detail="New password cannot be the same as your current password.")
    
    res = await partial_update_user_db(user_id, {"password_hash": get_hash(new_password)}, conn)

    if res.split()[1] == "1":
        access_payload = create_access_token(user["email"])
        refresh_payload = create_refresh_token(user["email"])

        res = {
                "access_token": access_payload["token"],
                "expires_at": access_payload["expires"], 
            }

        response = JSONResponse(content=res)
        response.set_cookie(
            key="refresh_token",
            value=refresh_payload["refresh_token"],
            httponly=True,
            # secure=False, #For dev phase  
            samesite="None",
            max_age=7*24*60*60
        )

        return response

    
    