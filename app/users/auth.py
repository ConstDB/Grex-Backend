from fastapi import HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
import os
import time


load_dotenv()

# JWT config
JWT_SECRET = os.getenv("JWT_SECRET")
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


def signJWT(user_id:str):
    try:
        payload = {
            "id" : user_id,
            "expires": time.time() + 1200
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return token
    except Exception as e:
        return { "message": f"Failed to encode token -> {e}"}


def decodeJWT(token:str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        return { "message": f"Failed to decode token -> {e}"}

#Google OAuth config

oauth = OAuth()
oauth.register(
    name="grex",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={"scope": "openid profile email"}
)

