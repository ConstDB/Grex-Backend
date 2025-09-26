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

class RefreshToken(BaseModel):
    refresh_token: str    

class EmailObject(BaseModel):
    email: str

class ResetPasswordPayload(BaseModel):
    email: str
    otp: str
    password_hash: str