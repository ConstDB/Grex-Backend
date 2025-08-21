from pydantic import BaseModel
from typing import Optional
from datetime import date 
import asyncpg

class WorkspaceCreation(BaseModel):
    name: str
    description: str
    project_nature: str
    start_date: date
    due_date: date
    created_by: int
    
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
   
