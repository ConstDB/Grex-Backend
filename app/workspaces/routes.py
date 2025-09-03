from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
import asyncpg
from ..workspaces.schemas import WorkspaceCreation, GetWorkspaceInfo, GetWorkspaces,UserDetail
from .crud import add_workspace_to_db, get_all_user_workspaces,  workspace_add_member,  kick_member, get_user_info, get_workspace_from_db, insert_members_read_status, search_member_by_name,update_user_data
import json
router = APIRouter()


# ===========================POST========================================================================

@router.post("")
async def create_workspace(workspace: WorkspaceCreation, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        workspace_dict = workspace.model_dump()
        
        res = await add_workspace_to_db(workspace_dict, conn)
        return res
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Workspace creation failed -> {e}")     
      
@router.post("/{workspace_id}/members")
async def add_workspace_member(email:str, workspace_id: int, conn: asyncpg.Connection = Depends(get_db_connection)):
    try: 
        user = await get_user_info(email, conn)
        user_dict = dict(user)

        member = {
            "workspace_id" : workspace_id,
            "user_id" : user_dict["user_id"],
            "role" : 'member',
            "nickname" : user_dict["first_name"],
        }

        member_read_status = {
            "workspace_id": workspace_id,
            "user_id" : user_dict["user_id"]
        }
        
        await insert_members_read_status(member_read_status, conn)
        res = await workspace_add_member(member,  conn)
        
        return res 
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}") 
    
# ===========================GET======================================================================
   
@router.get("/{user_id}", response_model=List[GetWorkspaces])
async def get_all_workspaces(user_id:int, conn: asyncpg.Connection = Depends(get_db_connection)):
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
     

@router.get("/{workspace_id}/{user_id}")
async def get_workspace_info(user_id:int, workspace_id:int, conn: asyncpg.Connection = Depends(get_db_connection)): 
    try:
        workspace = await get_workspace_from_db(user_id, workspace_id, conn)

        if workspace is None:
            raise HTTPException(status_code=404, detail=f"user does not belong on given workspace")
        
        info = dict(workspace)
        info["members"] = json.loads(info["members"])  

              
        return info
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
     
@router.get("{workspace_id}/members/search")
async def get_workspace_members(workspace_id: int, name: str, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        return await search_member_by_name(name, workspace_id, conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workspace members -> {e}")

        


# ===========================PUUTA======================================================================


     
@router.patch("/workspace/{workspace_id}")
async def workspace_update_data(workspace_id: int, user_id: int, role: str, project_nature: str,Description : str, nickname: str,  conn: asyncpg.Connection=Depends(get_db_connection)):
    try:
        res = await update_user_data(
            workspace_id=workspace_id,
            user_id=user_id,
            project_nature=project_nature,
            Description=Description,
            role=role,
            nickname=nickname,
            conn=conn
        )

        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Process failed -> {e}")

 #===========================DELETE=====================================================================
@router.delete("/{workspace_id}/members")
async def workspace_kick_member(workspace_id: int, user_id:int, conn: asyncpg.Connection = Depends(get_db_connection)): 
    try: 
        res = await kick_member(workspace_id, user_id, conn)
        
        return res 
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
     

