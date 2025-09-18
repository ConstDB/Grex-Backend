from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime



class GetLinks(BaseModel):
    link_id:int
    workspace_id:int
    message_id: Optional[int] = None
    link_name: str
    link_url:str
    created_at: datetime
