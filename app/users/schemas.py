from pydantic import BaseModel
from typing import Optional


class UserRegisterSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password_hash: str
    


class UserLoginSchema(BaseModel):
    email: str
    password_hash: str


class UserInformation(BaseModel):
    user_id: int # change to str later
    first_name: str
    last_name: str
    email: str
    password_hash: str
    phone_number: str
    profile_picture: Optional[str] = None
    status: str

class RefreshToken(BaseModel):
    refresh_token: str    

class EmailObject(BaseModel):
    email: str