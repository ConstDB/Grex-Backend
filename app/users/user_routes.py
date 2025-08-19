from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import UserLoginSchema, UserRegisterSchema, UserInformation, RefreshToken
from .auth import verify_password, get_password_hash, create_access_token, create_refresh_token, token_response, oauth, decode_refresh_token
from authlib.integrations.starlette_client import OAuth
from ..db.database import Database
from ..deps import get_db_connection
from .crud import add_user_to_db, get_user_from_db
import logging
import asyncpg
import os

router = APIRouter()



logger = logging.getLogger("uvicorn")

@router.get("/testing")
async def Testing():
    return "hello this is users route"