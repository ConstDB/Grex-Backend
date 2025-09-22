from fastapi import APIRouter, Depends, HTTPException
from .schemas import GetUserWithLinksResponse, PatchUserResponse
from ..deps import get_db_connection
from .crud import fetch_users_by_name
from .services import get_user_data_service, partial_update_user_service, get_user_tasks_services
from ..authentication.services import get_current_user
from ..utils.normalizer import normalize_name
import asyncpg

router = APIRouter()

@router.get("/users/search")
async def search_users(name:str, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        users = await fetch_users_by_name(normalize_name(name), conn)
        if users is None:
            raise HTTPException(status_code=404, detail=f"There's no users found with name {name}.")
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search for users -> {e}")

@router.get("/user/{user_id}/profile", response_model=GetUserWithLinksResponse)
async def get_user_data_route(user_id: int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        users = await get_user_data_service(user_id, conn)
        
        return users
    except Exception as e: 
        raise HTTPException (status_code=500, detail=f"Failed to get User Data -> {e}")
    
@router.patch("/user/{user_id}/profile")
async def update_user_info_route(user_id:int, model: PatchUserResponse, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try: 
        users = await partial_update_user_service(user_id, model.model_dump(), conn)
         
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Process Failed -> {e}")

# Get All user tasks for analytics
@router.get("/users/{user_id}/tasks")
async def get_user_tasks_route(user_id: int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    return await get_user_tasks_services(user_id, conn)