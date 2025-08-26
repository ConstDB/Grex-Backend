from pydantic import BaseModel, AwareDatetime
from typing import Optional
from datetime import datetime


class UserRegisterSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password_hash: str
    


class UserLoginSchema(BaseModel):
    email: str
    password_hash: str


class UserBasic(BaseModel):
    user_id: int
    profile_picture: Optional[str] = None
    status: Optional[str] = None

class UserDetail(BaseModel):
    user_id: int 
    role : str
    nickname :str
    joined_at : AwareDatetime
    first_name: str
    last_name: str
    email: str
    profile_picture: Optional[str] = None
    status: Optional[str] = None
    phone_number: Optional[str] = None
class RefreshToken(BaseModel):
    refresh_token: str    