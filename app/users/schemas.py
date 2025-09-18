from pydantic import BaseModel, AwareDatetime
from typing import Optional


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

class EmailObject(BaseModel):
    email: str
    
class GetUserResponse(BaseModel):
    first_name:str
    last_name:str
    email:str
    phone_number:Optional[str] = None
    profile_picture:Optional[str] = None
    

class PatchUserResponse(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password_hash: Optional [str] = None
    profile_picture: Optional[str] = None
    
    