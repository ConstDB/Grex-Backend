# app/api/task/crud/task_crud.py

# Assigning users to a specific task
async def create_taskassignment(conn, task_id, user_id):
    query = """
            INSERT INTO task_assignments(task_id, user_id)
            VALUES ($1, $2)
            RETURNING task_id, user_id
        """
    row = await conn.fetchrow(query, task_id, user_id)
    return dict(row)

# Get assigned users from a task
async def get_taskassignment(conn, task_id):
    query = """
            SELECT *
            FROM task_assignments
            WHERE task_id = $1 
        """
    rows = await conn.fetch(query, task_id)
    return [dict(row) for row in rows] if rows else None

# Unassign users from task
async def delete_taskassignment(conn, task_id:int, user_id:int):
    query = "DELETE FROM task_assignments WHERE task_id=$1 AND user_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, user_id)
    return dict(row) if row else None
