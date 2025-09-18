from pydantic import BaseModel, AwareDatetime
from typing import Optional

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
    
    