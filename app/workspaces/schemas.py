from pydantic import BaseModel
from typing import Optional, List
from ..users.schemas import UserBasic, UserDetail
from datetime import date, datetime

class WorkspaceCreation(BaseModel):
    name: str
    description: str
    project_nature: str
    start_date: date
    due_date: date
    created_by: int  
    
    
class GetWorkspaces (BaseModel):
    
    workspace_id: int
    name: str
    project_nature: Optional[str] = None
    start_date: Optional[date]=None
    due_date: Optional[date]=None
    created_by: int 
    workspace_profile_url: Optional[str] = None
    members: List[UserBasic]
    
class GetWorkspaceInfo (BaseModel):
    
    workspace_id: int
    name: str
    project_nature: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date]=None
    due_date: Optional[date]=None
    workspace_profile_url: Optional[str] = None
    created_by: int 
    created_at: datetime
    members: List[UserDetail]
    
class WorkspaceAddMember(BaseModel):
    workspace_id: int
    email: str
class WorkspaceChangeRole(BaseModel):
    workspace_id: int 
    user_id: str
    role: str 
    nickname:str
   # members:[WorkspaceMember] 
class WorkspaceKickMember(BaseModel):
    workspace_id: int
    user_id: str
class WorkspaceChangeNickname(BaseModel):
    workspace_id: int
    user_id: int
    nickname: str
class WorkspacePutUpdate(BaseModel):
    workspace_id: int
    name: str
    description: str
    project_nature:str
    start_date:date
    due_date: date
    leader_id: str
    created_at: date 
class WorkspacePatchUpdate(BaseModel):
    workspace_id:int
    name: str
    due_date: date 


    

   
