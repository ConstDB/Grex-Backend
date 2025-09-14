# app/api/task/crud/task_crud.py

from ...task.schemas.Tasks_schema import TaskCreate, TaskPatch, TaskCreateOut, TaskAllOut
from fastapi import HTTPException
from datetime import datetime, timezone
from ...utils.decorators import db_error_handler
from ...utils.task_logs import log_task_action


now = datetime.now(timezone.utc)


@db_error_handler
async def create_task(conn, workspace_id: int, task: TaskCreate):
    status = task.status or "pending"
    priority = task.priority_level or "low"

    valid_status = {"pending", "done", "overdue"}
    valid_priority = {"low", "medium", "high"}

    if status not in valid_status:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_status}")
    if priority not in valid_priority:
        raise ValueError(f"Invalid priority: {priority}. Must be one of {valid_priority}")

    user_exists = await conn.fetchrow(
        "SELECT user_id FROM users WHERE user_id = $1", task.created_by
    )
    if not user_exists:
        raise HTTPException(status_code=404, detail=f"User with id {task.created_by} does not exist")
    
    # fallback to "General"
    category = task.category or "General"

    # Look up the actual category_id from categories
    category_id = await conn.fetchval(
        """
        SELECT category_id 
        FROM categories 
        WHERE workspace_id = $1 AND name = $2
        """,
        workspace_id, category
    )

    if not category_id:
        raise ValueError(f"Category '{category}' not found in workspace {workspace_id}")
    
    query = """
    WITH inserted AS (
        INSERT INTO tasks 
        (workspace_id, category_id, title, subject, description, deadline, status, priority_level, start_date, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING *
    )
    SELECT 
        c.name AS category,
        i.task_id,
        i.workspace_id,
        i.title,
        i.subject,
        i.description,
        i.deadline,
        i.status,
        i.priority_level,
        i.start_date,
        i.created_by,
        i.created_at
    FROM inserted i
    LEFT JOIN categories c ON i.category_id = c.category_id;
    """
    
    row = await conn.fetchrow(query, 
                              workspace_id,
                              category_id, 
                              task.title, 
                              task.subject, 
                              task.description, 
                              task.deadline, 
                              status, 
                              priority, 
                              task.start_date, 
                              task.created_by)

    task_id = row['task_id']

    # Log the creation
    content = (
        f"Leader {task.created_by} created task '{task.title}' "
        f"(task_id: {task_id}) with description '{task.description}', deadline: {task.deadline.isoformat()}."
    )
    await log_task_action(conn, workspace_id, content)
    
    return TaskCreateOut(**dict(row))



@db_error_handler
async def get_task(conn, workspace_id: int, task_id: int):
    query = """
        SELECT 
            t.task_id,
            t.workspace_id,
            t.category_id,
            c.name AS category,
            t.subject,
            t.title,
            t.description,
            t.deadline,
            t.status,
            t.priority_level,
            t.start_date,
            t.created_by,
            t.created_at,
            t.marked_done_at
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.category_id
        WHERE t.workspace_id = $1 AND t.task_id = $2
    """
    row = await conn.fetchrow(query, workspace_id, task_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found in workspace {workspace_id}")
    row = dict(row)
    if row.get("category") is None:
        row["category"] = "General"
    return TaskAllOut(**row)


@db_error_handler
async def get_tasks_by_workspace(conn, workspace_id: int):
    query = """
        SELECT 
            t.task_id,
            t.workspace_id,
            t.category_id,
            c.name AS category,
            t.subject,
            t.title,
            t.description,
            t.deadline,
            t.status,
            t.priority_level,
            t.start_date,
            t.created_by,
            t.created_at,
            t.marked_done_at
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.category_id
        WHERE t.workspace_id = $1
        ORDER BY t.created_at DESC
    """
    rows = await conn.fetch(query, workspace_id)
    return [TaskAllOut(**dict(r)) for r in rows]


@db_error_handler
async def patch_task(
    conn,
    workspace_id: int,
    task_id: int,
    patch_task: TaskPatch
):
    # Get only the provided fields
    update_data = patch_task.model_dump(exclude_unset=True) # Get only the provided fields

    if not update_data:
        return {"status": "no changes"}

    updated_by = update_data.pop("updated_by", None)

    # translate 'category' to 'category_id' for db to understand
    if "category" in update_data: 
        category_name = update_data.pop("category")

        category_id = await conn.fetchval(
            "SELECT category_id FROM categories WHERE workspace_id=$1 AND name=$2",
            workspace_id, category_name
        )

        if not category_id:
            raise ValueError(f"Category '{category_name}' not found in workspace {workspace_id}")

        update_data["category_id"] = category_id

    # fetch current task to be patched
    current_task = await conn.fetchrow(
        "SELECT * FROM tasks WHERE task_id=$1 AND workspace_id=$2",
        task_id, workspace_id
    )

    if not current_task:
        return None

    # finds the fields that were actually changed
    changed_fields = {
        field: value
        for field, value in update_data.items()
        if value != current_task[field]
    }

    if not changed_fields:
        return {"status": "no actual changes"}

    # builds the SQL uddates
    set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(changed_fields.keys())])
    values = list(changed_fields.values())

    #  Use a Common Table Expression (CTE) so we can update AND immediately use the updated row/s
    query = f"""
    WITH updated AS (
        UPDATE tasks t
        SET {set_clause}
        WHERE t.task_id = ${len(values)+1}
          AND t.workspace_id = ${len(values)+2}
        RETURNING *
    )
    SELECT 
        c.name AS category,
        u.task_id,
        u.workspace_id,
        u.title,
        u.subject,
        u.description,
        u.deadline,
        u.status,
        u.priority_level,
        u.start_date,
        u.created_by,
        u.created_at,
        u.marked_done_at
    FROM updated u
    LEFT JOIN categories c ON u.category_id = c.category_id;
"""

    row = await conn.fetchrow(query, *values, task_id, workspace_id)

    if not row:
        return None

    # build the changed logs
    log_changes = []
    for field, value in changed_fields.items():
        old_val = current_task[field]

        if field == "category_id":
            old_cat = await conn.fetchval("SELECT name FROM categories WHERE category_id=$1", old_val)
            new_cat = await conn.fetchval("SELECT name FROM categories WHERE category_id=$1", value)
            log_changes.append(f"category changed from '{old_cat}' to '{new_cat}'")
        else:
            log_changes.append(f"{field} changed from '{old_val}' to '{value}'")

    # write the task_logs
    if log_changes:
        changes = ", ".join(log_changes)
        actor = updated_by or "Leader"
        content = f"{actor} patched task_id {task_id}. Changes: {changes}"
        await log_task_action(conn, workspace_id, content)

        notif_row = await conn.fetchrow(
            """
            INSERT INTO notifications (content, workspace_id)
            VALUES ($1, $2)
            RETURNING notification_id
            """,
            f"A task {task_id} has been modified. {changes}", 
            workspace_id
        )
        if notif_row:
            await conn.execute(
                """
                INSERT INTO notification_recipients(notification_id, user_id, is_read)
                SELECT $1, ta.user_id, FALSE
                FROM task_assignments ta
                WHERE ta.task_id = $2
                """,
                notif_row["notification_id"], task_id
            )

    return dict(row)


@db_error_handler
async def delete_task(conn, workspace_id: int, task_id: int):
    query = "DELETE FROM tasks WHERE task_id=$1 AND workspace_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, workspace_id)

    if not row:
        return None  # task not found
    
    content = (
        f"A workspace Leader deleted task_id: {row['task_id']}"
    )
    await log_task_action(conn, workspace_id, content)
    return dict(row)