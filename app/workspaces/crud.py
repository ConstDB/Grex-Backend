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

async def get_all_workspaces_to_db(user_id: int, conn: asyncpg.Connection):
    try:
        query = """SELECT * FROM workspaces WHERE user_id = $1"""
        res = await conn.fetch(query, user_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")

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
      