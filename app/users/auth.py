from fastapi import HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from passlib.context import CryptContext
from dotenv import load_dotenv
from ..config.settings import settings as st
import jwt
import os
import time


load_dotenv()

# JWT config
JWT_ACCESS_SECRET = st.JWT_ACCESS_SECRET
JWT_REFRESH_SECRET = st.JWT_REFRESH_SECRET
JWT_ALGORITHM = st.JWT_ALGORITHM
pwd_content = CryptContext(schemes=["bcrypt"])


def token_response(token:str):
    """
        Getter function for token(access/refresh)
    """
    return{
        "Access_token" : token
    }

def get_password_hash(password:str):
    """
        encrypts passwords
    """
    return pwd_content.hash(password)

def verify_password(plain_password:str, hashed_password:str):
    """
        compares plain and hashed password if they are identical
    """
    return pwd_content.verify(plain_password, hashed_password)


def create_access_token(email:str, expires = time.time() + 1200):
    """
        generates access_token(short-lived) that will be used on accessing endpoints
    """

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
    """
        generates refresh_token(long-lived) that will be used on generating new access token once it expired
    """

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
    """
        decodes the token(access) from jwt to dict object and also checks if its expired
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode token -> {e}")


def decode_refresh_token(token:str):
    """
        decodes the token(refresh) from jwt to dict object and also checks if its expired
    """

    try:
        decoded_token = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["refresh_token_expires_at"] >= time.time() else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode token -> {e}")

#Google OAuth config

oauth = OAuth()
oauth.register(
    name="grex",
    client_id=st.GOOGLE_CLIENT_ID,
    client_secret=st.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={"scope": "openid profile email"}
)

