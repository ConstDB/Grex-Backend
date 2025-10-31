from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CreateLinks(BaseModel):
    link_name: str
    link_url: str


class GetLinks(BaseModel):
    link_id:int
    workspace_id:int
    link_name: str
    link_url:str
    created_at: datetime

class PutLink(BaseModel):
    link_name:Optional[str] = None
    link_url:Optional[str] = None