from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class CategoryBaseModel (BaseModel):
    name: str

class CategoryCreate(CategoryBaseModel):
    pass

class CategoryUpdate(BaseModel):
    name: str

class CategoryDelete(BaseModel):
    status: str
    message: str

class CategoryOut(CategoryBaseModel):
    workspace_id: int
    category_id: int
    name: str
    created_at: datetime
