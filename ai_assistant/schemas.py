from pydantic import BaseModel, Field


class QueryPayload(BaseModel):
    role: str = Field(...)
    nickname: str = Field(...)
    query : str = Field(...)
    workspace_id : int = Field(...)