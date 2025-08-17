from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import UserLoginSchema, UserRegisterSchema, UserInformation, RefreshToken
from .auth import verify_password, get_password_hash, create_access_token, create_refresh_token, token_response, oauth, decode_refresh_token
from authlib.integrations.starlette_client import OAuth
from ..db.database import Database
from ..deps import get_db_connection
from .crud import add_user_to_db, get_user, update_refresh_token
import logging
import asyncpg
from ..config.settings import settings as st
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
        user_dict["refresh_token_expires_at"] = refresh_payload["refresh_token_expires_at"]
        user_dict["revoked"] = refresh_payload["revoked"]

        # get the user infos from DB
        raw = await add_user_to_db(user_dict, conn)

        # then convert it into dict
        user_data = dict(raw)

        # Construct response
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

        # Get token payloads
        access_payload = create_access_token(user.email)
        refresh_payload = create_refresh_token(user.email)

        # Get user data from DB    
        raw = await get_user(user_dict["email"], conn, fetch="user_id, first_name, last_name, email, profile_picture, phone_number, status, password_hash") 
        

        if raw is None:
            raise HTTPException(status_code=404, detail="User does not exists.")

        if not verify_password(user_dict["password_hash"], raw["password_hash"]):
            raise HTTPException(status_code=401, detail="Wrong email or password.")
 
        # Updates the refresh_token related attributes to the DB
        update_token = await update_refresh_token(user_id= raw["user_id"], payload=refresh_payload, conn=conn)
        
        user_data = dict(raw)
        user_data.pop("password_hash")

        response = {
            "user": user_data,
            "access_token": access_payload["token"],
            "refresh_token": refresh_payload["refresh_token"],
            "expires_at": access_payload["expires"] #UNIX timestamp
        }
 
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User login failed. -> {e}")

@router.post("/auth/refresh")
async def refresh_token(token: RefreshToken, conn: asyncpg.Connection = Depends(get_db_connection)):
    """
        will be called once the access_token is expired
    """
    try:
        #checks if the token is still valid
        refresh_token = decode_refresh_token(token.refresh_token)

        if refresh_token is None:
            raise HTTPException(status_code=401, detail=f"refresh token expired")
        # get the user data and validates if the token is already revoked
        user = await get_user(refresh_token["email"], conn, fetch="refresh_token, revoked")
        if user["refresh_token"] != token.refresh_token or user["revoked"] == True:

            raise HTTPException(status_code=401, detail=f"token either revoked or invalid")

        # generate new access token and remove the expires on the payload
        new_access_token = create_access_token(refresh_token["email"])
        new_access_token.pop("expires")

        return new_access_token

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to renew token -> {e}")

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
            "password_hash": get_password_hash(st.SECRET_PASSWORD),
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
