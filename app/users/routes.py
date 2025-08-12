from fastapi import APIRouter, Depends, HTTPException
from .schemas import UserLoginSchema, UserRegisterSchema, UserInformation
from .auth import verify_password, get_password_hash, signJWT, token_response
from ..db.database import Database
from ..deps import get_db_connection
from .crud import add_user_to_db, get_user
import asyncpg

router = APIRouter()


@router.get("/testing")
async def Testing():
    return "hello this is users route"


@router.post("/sign-up")
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
        raise HTTPException(status_code=500, detail="User creation failed. -> {e}")
    
    

@router.post("/login")
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
    