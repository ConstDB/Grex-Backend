from pydantic import BaseModel, AwareDatetime
from typing import Optional, List

class UserBasic(BaseModel):
    user_id: int
    profile_picture: Optional[str] = None


class UserDetail(BaseModel):
    user_id: int 
    role : str
    nickname :str
    joined_at : AwareDatetime
    first_name: str
    last_name: str
    email: str
    profile_picture: Optional[str] = None
    phone_number: Optional[str] = None

class GetLinksResponse(BaseModel):
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    twitter: Optional[str] = None
    discord: Optional[str] = None
    email: Optional[str] = None



class GetUserResponse(BaseModel):
    user_id: int
    first_name:str
    last_name:str
    email:str
    phone_number:Optional[str] = None
    profile_picture:Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    
class GetUserWithLinksResponse(GetUserResponse):
    social_links: GetLinksResponse
    

class PatchUserResponse(BaseModel):
    first_name:Optional[str] = None 
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number:Optional[str] = None
    profile_picture:Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    social_links: Optional[GetLinksResponse] = None
    
class PasswordPayload(BaseModel):
    old_password: str
    new_password: str

