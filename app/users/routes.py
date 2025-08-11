from fastapi import APIRouter, Depends
from .schemas import UserLoginSchema, UserRegisterSchema
from .auth import verify_password, get_password_hash, signJWT, token_response
from ..db.database import Database
from ..deps import get_db_connection
from .crud import add_user_to_db
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

        password = get_password_hash(user.password)

        user_dict["password"] = password
        await add_user_to_db(user_dict, conn)
        return access_token

    except Exception as e:
        return {"message":f"User creation failed. -> {e} "}
    

    

@router.post("/login")
async def login(user: UserLoginSchema):
    pass