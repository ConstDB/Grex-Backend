from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
from ..workspaces.schemas import WorkspaceCreation, GetWorkspaces, WorkspacePatch, WorkspaceMembersPatch
from ..authentication.services import get_current_user
from .crud import add_workspace_to_db, get_all_user_workspaces,  workspace_add_member,  kick_member, get_user_info, get_workspace_from_db, insert_members_read_status, fetch_workspace_members_db, update_workspace_data, update_user_data
import json
import asyncpg

router = APIRouter()


# ===========================POST========================================================================

@router.post("/workspace")
async def create_workspace(workspace: WorkspaceCreation, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)): 
    try:
        workspace_dict = workspace.model_dump()
        
        res = await add_workspace_to_db(workspace_dict, conn)
        return res
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Workspace creation failed -> {e}")     
      
@router.post("/workspace/{workspace_id}/members")
async def add_workspace_member(email:str, workspace_id: int, added_by: int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try: 
        user = await get_user_info(email, conn)
        user_dict = dict(user)

        member = {
            "workspace_id" : workspace_id,
            "user_id" : user_dict["user_id"],
            "role" : 'member',
            "nickname" : user_dict["first_name"],
            "added_by": added_by
        }

        member_read_status = {
            "workspace_id": workspace_id,
            "user_id" : user_dict["user_id"]
        }
        
        res = await workspace_add_member(member,  conn)
        await insert_members_read_status(member_read_status, conn)
        
        return res 
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}") 
    
# ===========================GET======================================================================
   
@router.get("/users/{user_id}/workspace", response_model=List[GetWorkspaces])
async def get_all_workspaces(user_id:int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        
        workspaces = await get_all_user_workspaces(user_id, conn)
        
        processed_data = []
        
        for workspace in workspaces:
            data = dict(workspace)
            data["members"] = json.loads(data["members"])
            processed_data.append(data)
        
        return [GetWorkspaces(**dict(data)) for data in processed_data]
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
     

@router.get("/workspace/{workspace_id}")
async def get_workspace_info(workspace_id:int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)): 
    try:
        workspace = await get_workspace_from_db(workspace_id, conn)

        if workspace is None:
            raise HTTPException(status_code=404, detail=f"user does not belong on given workspace")
        
        return workspace
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
     
@router.get("/workspace/{workspace_id}/members")
async def get_workspace_members(workspace_id: int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        return await fetch_workspace_members_db(workspace_id, conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workspace members -> {e}")       
     

# ===========================PATCH======================================================================
@router.patch("/workspace/{workspace_id}")
async def workspace_update (workspace_id: int, model: WorkspacePatch, conn: asyncpg.Connection=Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        res = await update_workspace_data (workspace_id, model.model_dump(),  conn)    
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Process failed -> {e}")
    
@router.patch("/workspace/{workspace_id}/members/{user_id}")
async def workspace_user_update(workspace_id: int, user_id: int, model: WorkspaceMembersPatch, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)):
    try:
        res = await update_user_data(workspace_id, user_id, model.model_dump(), conn)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"process failed->{e}")


 #===========================DELETE=====================================================================
@router.delete("/workspace/{workspace_id}/members")
async def workspace_kick_member(workspace_id: int, user_id:int, conn: asyncpg.Connection = Depends(get_db_connection), token: str = Depends(get_current_user)): 
    try: 
        res = await kick_member(workspace_id, user_id, conn)
        
        return res 
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
     

