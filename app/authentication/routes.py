from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import UserLoginSchema, UserRegisterSchema, EmailObject, ResetPasswordPayload
from fastapi.responses import JSONResponse
from .services import verify_hash, get_hash, create_access_token, create_refresh_token, oauth, decode_refresh_token, forgot_password_service, reset_password_service
from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordRequestForm
from ..deps import get_db_connection
from .crud import add_user_to_db, get_user_from_db, update_refresh_token_on_db, revoke_user_token_on_db, insert_social_links_db
import asyncpg
from ..config.settings import settings as st

router = APIRouter()

@router.post("/auth/token")
async def issue_token(form_data: OAuth2PasswordRequestForm = Depends()):
    
    if form_data.username != "test" and form_data.password != "password":
        raise HTTPException(status_code=401, detail=f"Wrong password or Username")

    access_payload = create_access_token(form_data.username) # get short-lived token from JWT
    refresh_payload = create_refresh_token(form_data.username)

    return {
        "access_token": access_payload["token"],
        "refresh_token": refresh_payload["refresh_token"],
        "token_type": "bearer"
    }
    


@router.post("/auth/sign-up")
async def sign_up(user: UserRegisterSchema, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        user_dict = user.model_dump() # convert object to dict

        access_payload = create_access_token(user.email) # get short-lived token from JWT
        refresh_payload = create_refresh_token(user.email)

        # add data that does not come from frontend to user_dict so it can be added on the DB as well
        user_dict["password_hash"] = get_hash(user.password_hash)
        user_dict["refresh_token"] = str(refresh_payload["refresh_token"])
        user_dict["refresh_token_expires_at"] = refresh_payload["refresh_token_expires_at"]
        user_dict["revoked"] = refresh_payload["revoked"]

        # insert and return the user infos from DB
        raw = await add_user_to_db(user_dict, conn)


        # then convert it into dict
        user_data = dict(raw)
        
        # insert social links
        data = {"user_id":user_data["user_id"]}
        social_links = await insert_social_links_db(data, conn)

        res = {
            "user": user_data,
            "access_token": access_payload["token"],
            "expires_at": access_payload["expires"], 
        }

        response = JSONResponse(content=res)
        response.set_cookie(
            key="refresh_token",
            value=refresh_payload["refresh_token"],
            httponly=True,
            samesite="None",
            # secure=False, # for dev phase
            max_age=7*24*60*60
        )

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

        # Get user data from DB    /
        raw = await get_user_from_db(user_dict["email"], conn, fetch="user_id, first_name, last_name, email, profile_picture, phone_number, password_hash") 
        

        if raw is None:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_hash(user_dict["password_hash"], raw["password_hash"]):
            raise HTTPException(status_code=401, detail="Wrong email or password.")
 
        # Updates the refresh_token related attributes to the DB
        update_token = await update_refresh_token_on_db(user_id= raw["user_id"], payload=refresh_payload, conn=conn)
        
        user_data = dict(raw)
        user_data.pop("password_hash")

        res = {
            "user": user_data,
            "access_token": access_payload["token"],
            "expires_at": access_payload["expires"], #UNIX timestamp
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User login failed. -> {e}")

@router.post("/auth/refresh")
async def refresh_token(email:EmailObject, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        email_dict = email.model_dump()
        
        res = await get_user_from_db(email=email_dict["email"], conn=conn, fetch="refresh_token, revoked")
        refresh_token = decode_refresh_token(res["refresh_token"])
    
        if res["revoked"] == True:
            raise HTTPException(status_code=401, detail=f"Refresh token revoked")

        new_access_token = create_access_token(refresh_token["sub"])

        return new_access_token

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to renew token -> {e}")


@router.post("/auth/logout")
async def logout(user_id: int, conn: asyncpg.Connection = Depends(get_db_connection)):
    
    try:
        payload = {
            "revoked" : True
        }
        result = await revoke_user_token_on_db(user_id, payload, conn)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to signout user -> {e}")
    
@router.post("/auth/forgot-password")
async def forgot_password_route(email:str, conn: asyncpg.Connection = Depends(get_db_connection)):
    await forgot_password_service(email, conn)
    return {"response" : "We’ve sent a one-time password (OTP) to your email. Enter it to proceed."}
    
    
@router.post("/auth/reset-password")
async def reset_password_route(payload: ResetPasswordPayload,  conn: asyncpg.Connection = Depends(get_db_connection)):
    res = await reset_password_service(payload=dict(payload), conn=conn)
    return res


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
            "password_hash": get_hash(st.SECRET_PASSWORD),
            "profile_picture" : user_info["picture"]
        }

        access_token = create_access_token(user_info["email"])
        existing_user = await get_user_from_db(user_info["email"], conn)
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
