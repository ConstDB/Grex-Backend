from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class CategoryBaseModel (BaseModel):
    category_id: int
    name: str
    created_at: datetime

class CategoryCreate(CategoryBaseModel):
    pass

class CategoryUpdate(BaseModel):
    name: str

class CategoryOut(CategoryBaseModel):
    workspace_id: str
    category_id: int
    name: str
    created_at: datetime
