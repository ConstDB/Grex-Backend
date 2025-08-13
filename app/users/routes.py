from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import UserLoginSchema, UserRegisterSchema, UserInformation
from .auth import verify_password, get_password_hash, signJWT, token_response, oauth
from authlib.integrations.starlette_client import OAuth
from ..db.database import Database
from ..deps import get_db_connection
from .crud import add_user_to_db, get_user
import asyncpg
import os

router = APIRouter()


@router.get("/testing")
async def Testing():
    return "hello this is users route"


@router.post("/auth/sign-up")
async def sign_up(user: UserRegisterSchema, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        user_dict = user.model_dump()

        access_token = signJWT(user.email)

        user_dict["password_hash"] = get_password_hash(user.password_hash)
        res = await add_user_to_db(user_dict, conn)

        res_dict = dict(res)
        res_dict["access_token"] = access_token
        return res_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed. -> {e}")
    
    

@router.post("/auth/login")
async def login(user: UserLoginSchema, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        user_dict = user.model_dump()
        access_token = signJWT(user.email)
        res = await get_user(user_dict["email"], conn) 

        res_dict = dict(res)
        res_dict["access_token"] = access_token

        if res is None:
            raise HTTPException(status_code=404, detail="User does not exists.")
        if not verify_password(user_dict["password_hash"], res["password_hash"]):
            raise HTTPException(status_code=401, detail="Wrong email or password.")
        return res_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User login failed. -> {e}")
    
# Oauth Routes


@router.get("/auth/google")
async def auth_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.grex.authorize_redirect(request, redirect_uri)
    

@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    token = await oauth.grex.authorize_access_token(request)
    user_info = token.get('userinfo')


    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")

    res = {
        "first_name": user_info["given_name"],
        "last_name" : user_info["family_name"],
        "email" : user_info["email"],
        "password": get_password_hash(os.getenv("SECRET_PASSWORD")),
        "profile_picture" : user_info["picture"]
    }

    