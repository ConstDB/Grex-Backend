from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import UserLoginSchema, UserRegisterSchema, UserInformation, RefreshToken
from .auth import verify_password, get_password_hash, create_access_token, create_refresh_token, token_response, oauth, decode_refresh_token
from authlib.integrations.starlette_client import OAuth
from ..db.database import Database
from ..deps import get_db_connection
from .crud import add_user_to_db, get_user_from_db
from .auth import get_current_user
from ..utils.logger import logger
import asyncpg
import os

router = APIRouter()


@router.get("/testing")
async def Testing():
    return "hello this is users route"


@router.post("/user/profile/{user_id}")
async def get_user_profile(user_id:int, token: str = Depends(get_current_user)):
    try:
        return "Hello"

    except Exception as e:
        raise HTTPException(status_code=500, detail={e})