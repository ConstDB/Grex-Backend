from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import UserLoginSchema, UserRegisterSchema, UserInformation
from .auth import verify_password, get_password_hash, create_access_token, create_refresh_token, token_response, oauth
from authlib.integrations.starlette_client import OAuth
from ..db.database import Database
from ..deps import get_db_connection
from .crud import add_user_to_db, get_user, update_refresh_token
import logging
import asyncpg
import os

router = APIRouter()



logger = logging.getLogger("uvicorn")

@router.get("/testing")
async def Testing():
    return "hello this is users route"


@router.post("/auth/sign-up")
async def sign_up(user: UserRegisterSchema, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        user_dict = user.model_dump() # convert object to dict

        access_payload = create_access_token(user.email) # get short-lived token from JWT
        refresh_payload = create_refresh_token(user.email)

        # add data that does not come from frontend to user_dict so it can be added on the DB as well
        user_dict["password_hash"] = get_password_hash(user.password_hash)
        user_dict["refresh_token"] = str(refresh_payload["refresh_token"])
        # logger.info(f"token: {user_dict["refresh_token"]}")
        user_dict["refresh_token_expires_at"] = refresh_payload["refresh_token_expires_at"]
        user_dict["revoked"] = refresh_payload["revoked"]

        raw = await add_user_to_db(user_dict, conn)

        user_data = dict(raw)
        logger.info(f"user_data: {user_data}")

        response = {
            "user": user_data,
            "access_token": access_payload["token"],
            "refresh_token": refresh_payload["refresh_token"],
            "expires_at": access_payload["expires"]
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed. -> {e}")
    
    

@router.post("/auth/login")
async def login(user: UserLoginSchema, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        user_dict = user.model_dump()
        access_payload = create_access_token(user.email)
        refresh_payload = create_refresh_token(user.email)

        raw = await get_user(user_dict["email"], conn) 
        
        if raw is None:
            raise HTTPException(status_code=404, detail="User does not exists.")
        if not verify_password(user_dict["password_hash"], raw["password_hash"]):
            raise HTTPException(status_code=401, detail="Wrong email or password.")
 
        update_token = await update_refresh_token(user_id= raw["user_id"], payload=refresh_payload, conn=conn)
        
        user_data = dict(raw)
        user_data.pop("password_hash")

        response = {
            "user": user_data,
            "access_token": access_payload["token"],
            "refresh_token": refresh_payload["refresh_token"],
            "expires_at": access_payload["expires"] #UNIX timestamp
        }

        # if raw is None:
        #     raise HTTPException(status_code=404, detail="User does not exists.")
        # if not verify_password(user_dict["password_hash"], raw["password_hash"]):
        #     raise HTTPException(status_code=401, detail="Wrong email or password.")
 
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User login failed. -> {e}")

# @router.post("/auth/refresh")
# async def refresh_token(payload:)

# Oauth Routes


@router.get("/auth/google")
async def auth_google(request: Request):
    redirect_uri = "http://localhost:5142/auth/google/callback"
    return await oauth.grex.authorize_redirect(request, redirect_uri)
    

@router.get("/auth/google/callback")
async def auth_google_callback(data: dict, request: Request, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        token = await oauth.grex.authorize_access_token(request, data={"code": data["code"]})
        user_info = token.get('userinfo')


        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to retrieve user info")

        res = {
            "first_name": user_info["given_name"],
            "last_name" : user_info["family_name"],
            "email" : user_info["email"],
            "password_hash": get_password_hash(os.getenv("SECRET_PASSWORD")),
            "profile_picture" : user_info["picture"]
        }

        access_token = signJWT(user_info["email"])
        existing_user = await get_user(user_info["email"], conn)
        user_dict = dict(existing_user)

        if not existing_user:
            user = await add_user_to_db(res, conn)
            user_dict = dict(user)
            user_dict["access_token"] = access_token
            return user
            
        user_dict["access_token"] = access_token

        return user_dict
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something Went Wrong -> {e}")
