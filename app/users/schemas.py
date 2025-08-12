from pydantic import BaseModel
from typing import Optional


class UserRegisterSchema(BaseModel):
    full_name: str
    email: str
    password_hash: str


class UserLoginSchema(BaseModel):
    email: str
    password_hash: str


class UserInformation(BaseModel):
    user_id: int # change to str later
    name: str
    email: str
    password_hash: str
    profile_picture: Optional[str] = None
    status: str

