import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection
from ..db_instance import db

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
                    BEGIN 
                        INSERT INTO workspace_members (user_id, workspace_id, nickname, role)
                        VALUES(NEW.created_by, NEW.workspace_id, 'Leader','leader');
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
            w.created_at,
            w.description,
            COALESCE(            
                json_agg(
                    json_build_object(
                        'user_id', u.user_id, 
                        'first_name', u.first_name,
                        'last_name', u.last_name,
                        'email', u.email,
                        'profile_picture', u.profile_picture,
                        'status', u.status,
                        'phone_number', u.phone_number                    )
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
                w.description,
                w.project_nature,
                w.start_date,
                w.due_date,
                w.created_by,
                w.created_at,
                w.description;
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
                w.start_date,
                w.due_date,
                w.created_by,
                w.workspace_profile_url, 
                COALESCE(            
                    json_agg(
                        json_build_object(
                            'user_id', u.user_id, 
                            'first_name', u.first_name,
                            'last_name', u.last_name,
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
                    w.description,
                    w.project_nature,
                    w.start_date,
                    w.due_date,
                    w.created_by,
                    w.created_at,    
                    w.workspace_profile_url;
        """
           
        res = await conn.fetchrow(query, workspace_id, user_id )
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")    

async def workspace_add_member(workspace_id: int, user_id:int,nickname:str, conn: asyncpg.Connection = Depends(get_db_connection)):
    try: 
        
        role = 'member'
        
        query = """
                INSERT INTO workspace_members (workspace_id, user_id, role, nickname)
                VALUES ($1, $2 , $3, $4)                  
                """
        res = await conn.execute(query, workspace_id, user_id, role, nickname )
        
        return res 
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
        
async def workspace_role_update(workspace_id: int, user_id: int, role:str, conn: asyncpg.Connection): 
    try:
        query = """
        UPDATE workspace_members
        SET role = $3
        WHERE workspace_id = $1 AND user_id = $2
        returning * ;
         """
    
        res = await conn.fetchrow(query, workspace_id, user_id, role) 
    
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Process failed -> {e}")      
            
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
