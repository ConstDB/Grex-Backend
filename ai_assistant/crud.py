from app.utils.query_builder import get_query, insert_query
import asyncpg
from fastapi import HTTPException

async def fetch_related_messages_db(message_id: list, conn: asyncpg.Connection):
    query = """
        SELECT tm.content, wm.nickname, wm.role FROM messages m
        LEFT JOIN text_messages tm ON m.message_id = tm.message_id
        LEFT JOIN workspace_members wm ON m.sender_id = wm.user_id AND m.workspace_id = wm.workspace_id
        WHERE m.message_id = ANY($1::int[])
    """
    return await conn.fetch(query, message_id)

async def fetch_previous_messages_db(workspace_id: int, conn: asyncpg.Connection, limit:int = 10):
    query="""
        SELECT tm.content, wm.nickname, wm.role FROM messages m
        LEFT JOIN text_messages tm ON m.message_id = tm.message_id
        LEFT JOIN workspace_members wm ON m.sender_id = wm.user_id AND m.workspace_id = wm.workspace_id
        WHERE m.workspace_id = $1
        ORDER BY m.message_id DESC
        LIMIT $2
    """

    res = await conn.fetch(query, workspace_id, limit)

    res.reverse()
    return res
    
async def fetch_related_task_logs_db(task_log_ids: list, conn: asyncpg.Connection):
    query = """
        SELECT context FROM task_logs
        WHERE task_log_id = ANY($1::int[])
    """    

    return await conn.fetch(query, task_log_ids)    

async def fetch_recent_tasks_db(workspace_id: int, conn: asyncpg.Connection, limit: int = 7):
    query = """
        SELECT 
            t.task_id,
            t.title,
            t.description,
            t.deadline,
            t.start_date,
            t.status,
            creator.first_name,
            COALESCE(
                json_agg(
                    json_build_object(
                        'user_id', assignees.user_id,
                        'first_name', assignees.first_name
                    )
                ) FILTER (WHERE assignees.user_id IS NOT NULL), '[]'
            ) AS assignees
        FROM tasks t
        LEFT JOIN users creator ON t.created_by = creator.user_id
        LEFT JOIN task_assignments ta ON t.task_id = ta.task_id
        LEFT JOIN users assignees ON ta.user_id = assignees.user_id
        WHERE t.workspace_id = $1
        GROUP BY t.task_id, creator.first_name
        ORDER BY t.task_id DESC
        LIMIT $2;

    """

    return await conn.fetch(query, workspace_id, limit)

async def insert_task_db(workspace_id:int, payload:dict, conn: asyncpg.Connection):
    category = payload["category"] or "General"

    category_id = await conn.fetchval(get_query("workspace_id", "name", fetch="category_id", table="categories"), workspace_id, category)

    payload.pop("category")
    payload["category_id"] = category_id
    payload["workspace_id"] = workspace_id

    query = insert_query(payload, "tasks")

    return await conn.fetchrow(query, *payload.values())
