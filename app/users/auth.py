from fastapi import HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
import os
import time


load_dotenv()

# JWT config
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
pwd_content = CryptContext(schemes=["bcrypt"])


def token_response(token:str):
    return{
        "Access_token" : token
    }

def get_password_hash(password:str):
    return pwd_content.hash(password)

def verify_password(plain_password:str, hashed_password:str):
    return pwd_content.verify(plain_password, hashed_password)


def create_access_token(email:str, expires = time.time() + 1200):
    try:
        payload = {
            "email" : email,
            "expires": expires # 20 minutes
        }

        payload["token"] = jwt.encode(payload, JWT_ACCESS_SECRET, algorithm=JWT_ALGORITHM)
        
        payload.pop("email")
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encode access token -> {e}")


def create_refresh_token(email:str, expires = time.time() + 7 * 24 * 60 * 60):
    try:
        payload = {
            "email" : email,
            "refresh_token_expires_at" : expires # 7 days
        }
        payload["refresh_token"] = jwt.encode(payload, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)
        
        payload.pop("email")
        payload["revoked"] = False
        
        return payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encode refresh token -> {e}")



def decode_access_token(token:str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode token -> {e}")


def decode_refresh_token(token:str):
    try:
        decoded_token = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["refresh_token_expires_at"] >= time.time() else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode token -> {e}")

#Google OAuth config

oauth = OAuth()
oauth.register(
    name="grex",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={"scope": "openid profile email"}
)

