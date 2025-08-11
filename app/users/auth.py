import jwt
from dotenv import load_dotenv
import os
import time
from fastapi import HTTPException
from passlib.context import CryptContext

load_dotenv()

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

        return token_response(token)
    except Exception as e:
        return { "message": f"Failed to encode token -> {e}"}


def decodeJWT(token:str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        return { "message": f"Failed to decode token -> {e}"}
