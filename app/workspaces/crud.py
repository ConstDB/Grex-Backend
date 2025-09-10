import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection
from ..utils.query_builder import insert_query
from ..db_instance import db
import datetime as date
from .schemas import WorkspacePatch,WorkspaceMembersPatch
async def add_workspace_to_db(workspace:dict, conn: asyncpg.Connection):
    try:
        query = """
            INSERT INTO workspaces (name, description, project_nature, start_date, due_date, created_by)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        res = await conn.fetchrow(query, *workspace.values())
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")

    
async def get_user_info(email:str, conn: asyncpg.Connection):
    try:
        query = """
            SELECT user_id, first_name FROM users WHERE email = $1
        """
        
        user = await conn.fetchrow(query, email)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot get user information: {e}")

async def workspace_trigger():         
    try:  
        async with  db.get_connection() as conn:
              
            function_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_proc WHERE proname = 'add_workspace_leader'
                );
            """)
                
            if not function_exists: 
                await conn.execute("""
                    CREATE OR REPLACE FUNCTION add_workspace_leader()
                    RETURNS TRIGGER AS $$
                    DECLARE
                        u_first_name TEXT;
                    BEGIN 

                        SELECT u.first_name INTO u_first_name
                        FROM users u 
                        WHERE u.user_id = NEW.created_by;

                        INSERT INTO workspace_members (user_id, workspace_id, nickname, role)
                        VALUES(NEW.created_by, NEW.workspace_id, u_first_name,'leader');

                        INSERT INTO categories (workspace_id, name)
                        VALUES(NEW.workspace_id, 'General');
                        
                        INSERT INTO message_read_status (workspace_id, user_id)
                        VALUES (NEW.workspace_id, NEW.created_by)
                        ON CONFLICT (workspace_id, user_id) DO NOTHING;

                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                    
            workspace_trigger_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'auto_add_workspace_leader'
                );
            """)
                    
            if not workspace_trigger_exists:
                await conn.execute("""
                    CREATE TRIGGER auto_add_workspace_leader
                    AFTER INSERT ON workspaces
                    FOR EACH ROW EXECUTE FUNCTION add_workspace_leader();                                
                """)
            await conn.close()
                  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trigger setup failed -> {e}")
      
async def get_all_user_workspaces(user_id: int, conn:asyncpg.Connection): 
    try:
        query ="""
        SELECT 
            w.workspace_id,
            w.name,
            w.project_nature,
            w.start_date,
            w.due_date,
            w.created_by,
            w.workspace_profile_url, 
            COALESCE(            
                json_agg(
                    json_build_object(
                        'user_id', u.user_id, 
                        'profile_picture', u.profile_picture,
                        'status', u.status ,                
                        'phone_number', u.phone_number,      
                        'nickname', wm.nickname
                        )
                ) FILTER (WHERE u.user_id IS NOT NULL),
                '[]'                   
            ) AS members
            FROM workspaces w
            LEFT JOIN workspace_members wm ON w.workspace_id = wm.workspace_id
            LEFT JOIN users u ON wm.user_id = u.user_id
            WHERE EXISTS(
                SELECT 1
                FROM workspace_members wm2
                WHERE wm2.workspace_id = w.workspace_id
                    AND wm2.user_id = $1
            ) 
            
            GROUP BY
                w.workspace_id,
                w.name,
                w.project_nature,
                w.start_date,
                w.due_date,
                w.created_by,
                w.workspace_profile_url;
        """            
        res = await conn.fetch(query, user_id) 
        
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")
    
async def get_workspace_from_db(user_id:int, workspace_id: int, conn: asyncpg.Connection):
    
    try:    
        query = """
            SELECT 
                w.workspace_id,
                w.name,
                w.project_nature,
                w.description,
                w.start_date,
                w.due_date,
                w.workspace_profile_url,
                w.created_by, 
                w.created_at,
                
                w.created_by,
                w.workspace_profile_url, 
        
                COALESCE(            
                    json_agg(
                        json_build_object(
                            'user_id', u.user_id, 
                            'role', wm.role,
                            'joined_at', wm.joined_at,
                            'first_name', u.first_name,
                            'last_name', u.last_name,
                             'nickname', wm.nickname,
                            'email', u.email,
                            'profile_picture', u.profile_picture,
                            'status', u.status
                              
                        )
                    ) FILTER (WHERE u.user_id IS NOT NULL),
                    '[]'                   
                ) AS members
                FROM workspaces w
                LEFT JOIN workspace_members wm ON w.workspace_id = wm.workspace_id
                LEFT JOIN users u ON wm.user_id = u.user_id
                WHERE w.workspace_id = $1
                AND EXISTS(
                    SELECT 1
                    FROM workspace_members wm2
                    WHERE wm2.workspace_id = w.workspace_id
                        AND wm2.user_id = $2
                        
                ) 
                
                GROUP BY
                    w.workspace_id,
                    w.name,
                    w.project_nature,
                    w.description,
                    w.start_date,
                    w.due_date,
                    w.workspace_profile_url,
                    w.created_by, 
                    w.created_at;
        """
           
        res = await conn.fetchrow(query, workspace_id, user_id )
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")    

async def workspace_add_member(payload:dict, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        query = """
                INSERT INTO workspace_members (workspace_id, user_id, role, nickname)
                VALUES ($1, $2 , $3, $4)                  
                """
        res = await conn.execute(query, *payload.values() )
        
        return res 
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")

async def insert_members_read_status(payload:dict, conn: asyncpg.Connection):
    try:
        query = insert_query(payload, "message_read_status")

        res = await conn.fetchrow(query, *payload.values())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add read status on this workspace: {e}")
            

async def search_member_by_name(name:str, workspace_id: int, conn: asyncpg.Connection):
    try:
        query="""
            SELECT
                u.user_id,
                u.first_name,
                u.last_name,
                wm.nickname, 
                u.email, 
                u.profile_picture
                
            FROM users u
            LEFT JOIN workspace_members wm ON u.user_id = wm.user_id AND wm.workspace_id = $2
            WHERE ((u.first_name || ' ' || u.last_name) ILIKE '%' || $1 || '%')
            AND wm.workspace_id = $2
        """

        res = await conn.fetch(query, name, workspace_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch workspace member -> {e}")
           
    

async def kick_member(workspace_id: int, user_id: int, conn: asyncpg.Connection):
    try: 
        query =  """
        DELETE FROM workspace_members 
        WHERE workspace_id = $1 AND user_id = $2
        RETURNING *
        """
        res = await conn.fetchrow(query, workspace_id, user_id)
        

        return res 
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
        
async def update_workspace_data(
    workspace_id: int,
    model : dict, 
    conn: asyncpg.Connection    
):
    
    workspace_update = []
    workspace_values = []
    idx = 1    
        
    name = model.get("name")
    project_nature = model.get("project_nature")
    description = model.get("description")
    start_date = model.get("start_date")
    due_date = model.get("due_date")
    workspace_profile_url = model.get("workspace_profile_url")
    created_by = model.get("created_by")
    created_at = model.get("created_at")
    
    
    if name is not None: 
        workspace_update.append (f"name = ${idx}")
        workspace_values.append(name)
        idx += 1
        
    if project_nature is not None: 
        workspace_update.append(f"project_nature = ${idx}")
        workspace_values.append(project_nature)
        idx +=1
        
    if description is not None: 
        workspace_update.append(f"description = ${idx}")
        workspace_values.append(description)
        idx +=1
    
    if start_date is not None: 
        workspace_update.append(f"start_date = ${idx}")
        workspace_values.append(start_date)
        idx +=1
        
    if due_date is not None: 
        workspace_update.append(f"due_date = ${idx}")
        workspace_values.append (due_date)
        idx +=1
        
    if workspace_profile_url is not None:
        workspace_update.append(f"workspace_profile_url = ${idx}")
        workspace_values.append(workspace_profile_url)
        idx +=1
        
    if created_by is not None: 
        workspace_update.append(f"created_by = ${idx}")
        workspace_values.append(created_by)
        idx+=1
        
    if created_at is not None: 
        workspace_update.append(f"created_at = ${idx}")
        workspace_values.append(created_at)
        idx+=1
        
                
    if not workspace_update:
       return None


    query = f"""
    
        UPDATE workspaces
            SET { ", " .join(workspace_update)}
        WHERE workspace_id = ${idx} 
        RETURNING *;
        """
        
    workspace_values.append(workspace_id)
    
    res = await conn.fetchrow(query, *workspace_values)
    return dict(res) if res else None


async def update_user_data(workspace_id:int, user_id: int, model: dict, conn: asyncpg.Connection): 
   
    user_update = []
    user_values = []
    idx = 1 
    
        
    nickname = model.get("nickname")
    role = model.get("role")
        
    if nickname is not None:
        user_update.append(f"nickname = ${idx}")
        user_values.append(nickname)
        idx +=1
        
    if role is not None:
        user_update.append(f"role = ${idx}")
        user_values.append(role)
        idx +=1

    if not user_update:
       return None


    query = f"""
    
        UPDATE workspace_members
            SET { ", " .join(user_update)}
        WHERE workspace_id  = ${idx}
        AND user_id= ${idx+1} 
        RETURNING *;
        """
        
    user_values.extend([workspace_id, user_id])
    
    res = await conn.fetchrow(query, *user_values)
    return dict(res) if res else None

async def search_member_by_name(name:str, workspace_id: int, conn: asyncpg.Connection):
    try:
        query="""
            SELECT
                u.user_id,
                u.first_name,
                u.last_name, 
                u.email, 
                u.profile_picture
            FROM users u
            LEFT JOIN workspace_members wm ON u.user_id = wm.user_id AND wm.workspace_id = $2
            WHERE ((u.first_name || ' ' || u.last_name) ILIKE '%' || $1 || '%')
            AND wm.workspace_id = $2
        """

        res = await conn.fetch(query, name, workspace_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch workspace member -> {e}")


