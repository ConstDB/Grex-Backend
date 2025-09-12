from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import UserLoginSchema, UserRegisterSchema, RefreshToken,PatchUserResponse,GetUserResponse
from .auth import verify_password, get_password_hash, create_access_token, create_refresh_token, token_response, oauth, decode_refresh_token
from authlib.integrations.starlette_client import OAuth
from ..db.database import Database
from ..deps import get_db_connection
from .authentication_crud import add_user_to_db, get_user_from_db
from .user_crud import get_users_by_name,get_user_data_db,update_user_information_db
from .auth import get_current_user
from ..utils.logger import logger
from ..utils.normalizer import normalize_name
import asyncpg
import os

router = APIRouter()

@router.get("/users/search")
async def search_users(name:str, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        users = await get_users_by_name(normalize_name(name), conn)
        if users is None:
            raise HTTPException(status_code=404, detail=f"There's no users found with name {name}.")
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search for users -> {e}")

@router.get("/user/{user_id}/profile", response_model = GetUserResponse)
async def get_user_data_route(user_id: int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        users = await get_user_data_db(user_id, conn)
        
        return dict (users)
    except Exception as e: 
        raise HTTPException (status_code=500, detail=f"Failed to get User Data -> {e}")
    
@router.patch("/user/{user_id}/profile")
async def update_user_info_route(user_id:int, model: PatchUserResponse, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try: 
        users = await update_user_information_db(user_id, model.model_dump(), conn)
         
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Process Failed -> {e}")
