from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from .crud import get_user_from_db, insert_otp_db, update_password_db, delete_pin_record_db, fetch_otp_db
from dotenv import load_dotenv
from ..config.settings import settings as st
from datetime import datetime, timedelta
from ..utils.email_handler import send_otp_to_email
import asyncpg
import jwt
import time
import pyotp

load_dotenv()

# JWT config
JWT_ACCESS_SECRET = st.JWT_ACCESS_SECRET
JWT_REFRESH_SECRET = st.JWT_REFRESH_SECRET
JWT_ALGORITHM = st.JWT_ALGORITHM
pwd_content = CryptContext(schemes=["bcrypt"])

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token:str = Depends(oauth_scheme)):
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
            )

        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"{e}")



def websocket_authentication(token:str = Depends(oauth_scheme)):
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None
        return payload
    except Exception as e:
            return None

def token_response(token:str):
    """
        Getter function for token(access/refresh)
    """
    return{
        "Access_token" : token
    }

def get_hash(text:str):
    """
        encrypts passwords
    """
    return pwd_content.hash(text)

def verify_hash(plain_text:str, hashed_text:str):
    """
        compares plain and hashed password if they are identical
    """
    return pwd_content.verify(plain_text, hashed_text)


def create_access_token(email:str):
    try:
        payload = {
            "sub": email,
            "exp": time.time() + 15 * 60,
            "type": "access"
        }
        token = jwt.encode(payload, JWT_ACCESS_SECRET, algorithm=JWT_ALGORITHM)
        return {"token": token, "expires": payload["exp"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encode access token -> {e}")


def create_refresh_token(email:str):
    """
        generates refresh_token(long-lived) that will be used on generating new access token once it expired
    """
    try:
        payload = {
            "sub" : email,
            "exp" : time.time() + 7 * 24 * 60 * 60, # 7 days
            "type" : "refresh"
        }
        token = jwt.encode(payload, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)
        return {"refresh_token": token, "refresh_token_expires_at":payload["exp"], "revoked": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encode refresh token -> {e}")



def decode_access_token(token:str):
    """
        decodes the token(access) from jwt to dict object and also checks if its expired
    """
    try:
        decoded_token = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode token -> {e}")


def decode_refresh_token(token:str):
    """
        decodes the token(refresh) from jwt to dict object and also checks if its expired
    """
    try:
        decoded_token = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode refresh token -> {e}")

async def forgot_password_service(email:str, conn: asyncpg.Connection):
    """
        Service for verifying the email and sending otp
    """

    user = await get_user_from_db(email, conn, fetch="user_id, first_name")
    await delete_pin_record_db(user["user_id"], conn)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = pyotp.TOTP(st.OTP_SECRET, interval=180).now()

    sent = send_otp_to_email(email, user["first_name"], otp)
    
    if sent:
        expires_at = datetime.now() + timedelta(minutes=3)

        user = await insert_otp_db(user["user_id"], get_hash(otp), expires_at, conn)

    
async def reset_password_service(payload: dict, conn: asyncpg.Connection):
    user = await get_user_from_db(payload["email"], conn, fetch="user_id, first_name, last_name, email, profile_picture, phone_number")

    user = dict(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    password = {"password_hash":get_hash(payload["password_hash"])}
    
    totp = pyotp.TOTP(st.OTP_SECRET, interval=180)
    
    pin = await fetch_otp_db(user["user_id"], conn)
    if not totp.verify(payload["otp"], valid_window=1) or not verify_hash(payload['otp'], pin):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    await delete_pin_record_db(user["user_id"], conn)
    res = await update_password_db(user["user_id"], password, conn)

    if res:
        access_payload = create_access_token(payload["email"])
        refresh_payload = create_refresh_token(payload["email"])

        res = {
                "user": user,
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

#Google OAuth config

oauth = OAuth()
oauth.register(
    name="grex",
    client_id=st.GOOGLE_CLIENT_ID,
    client_secret=st.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={"scope": "openid profile email"}
)

