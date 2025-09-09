from fastapi import HTTPException, Request, Depends
from authlib.integrations.starlette_client import OAuth
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from ..config.settings import settings as st
from ..utils.logger import logger
import jwt
import os
import time
import logging


load_dotenv()

# JWT config
JWT_ACCESS_SECRET = st.JWT_ACCESS_SECRET
JWT_REFRESH_SECRET = st.JWT_REFRESH_SECRET
JWT_ALGORITHM = st.JWT_ALGORITHM
pwd_content = CryptContext(schemes=["bcrypt"])

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token:str = Depends(oauth_scheme), is_HTTP = True):
    try:
        payload = decode_access_token(token)
        if payload is None:
            if is_HTTP:
                raise HTTPException(
                status_code=401,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return payload
    except Exception as e:
        if is_HTTP:
            raise HTTPException(status_code=401, detail=f"{e}")
        else:
            return None

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



#Google OAuth config

oauth = OAuth()
oauth.register(
    name="grex",
    client_id=st.GOOGLE_CLIENT_ID,
    client_secret=st.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={"scope": "openid profile email"}
)

