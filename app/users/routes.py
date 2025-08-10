from fastapi import APIRouter, Depends
from .schemas import UserLoginSchema, UserRegisterSchema
from .auth import verify_password, get_password_hash
from ..db.database import Database
from .crud import add_user_to_db
import asyncpg

db = Database()

router = APIRouter()


@router.get("/testing")
async def Testing():
    return "hello this is users route"


@router.post("/sign-up")
async def sign_up(user: UserRegisterSchema):
    user_dict = user.model_dump()
    password = get_password_hash(user.password)
    add_user_to_db(user_dict)
    

    

@router.post("/login")
async def login(user: UserLoginSchema):
    pass