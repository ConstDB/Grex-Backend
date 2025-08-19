from pydantic import BaseModel
from typing import Optional
from datetime import date 

class WorkspaceCreation(BaseModel):
    name: str
    description: str
    project_nature: str
    start_date: date
    due_date: date
    
class GetWorkSpaces(BaseModel):
    workspace_id : int
    name: str
    latest_message: str
    
class GetWorkspaceInfo (BaseModel):
    workspace_id: int
    name: str
    description: str
    project_nature: str
    start_date: date