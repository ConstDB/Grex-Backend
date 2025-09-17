from ...utils.decorators import db_error_handler
from ...notifications.events import push_notifications
from datetime import datetime

# Assigning users to a specific task
@db_error_handler
async def create_taskassignment(conn, task_id, user_id):
    query = """
        INSERT INTO task_assignments (task_id, user_id)
        VALUES ($1, $2)
        RETURNING task_id, user_id
    """
    row = await conn.fetchrow(query, task_id, user_id)
    
    if row:
        workspace_id = await conn.fetchval(
            "SELECT workspace_id FROM tasks WHERE task_id = $1",
            task_id
        )
        workspace_name = await conn.fetchval(
            "SELECT name FROM workspaces WHERE workspace_id = $1",
            workspace_id
        )
        task_name = await conn.fetchval(
            "SELECT title FROM tasks WHERE task_id = $1",
            task_id
        )
        notif_query = """
            INSERT INTO notifications (content, workspace_id)
            VALUES ($1, $2)
            RETURNING notification_id
        """
        notif_row = await conn.fetchrow(
            notif_query,
            f"You have been assigned to Task {task_id}.",
            workspace_id
        )
        if notif_row:
            task_assignments = await conn.fetch(
                "SELECT user_id FROM task_assignments WHERE task_id=$1", task_id
            )

            for u in task_assignments:
                recipient_row = await conn.fetchrow(
                    """
                    INSERT INTO notification_recipients (notification_id, user_id, is_read)
                    VALUES ($1, $2, FALSE)
                    RETURNING recipient_id, user_id, is_read, delivered_at
                    """,
                    notif_row["notification_id"],
                    u["user_id"]
                )

                await push_notifications(u["user_id"], {
                    "notification_id": notif_row["notification_id"],
                    "user_id": u["user_id"],
                    "recipient_id": recipient_row["recipient_id"],
                    "content": f"You have been assigned to Task {task_id}",
                    "workspace_name": workspace_name,
                    "is_read": recipient_row["is_read"],
                    "delivered_at": recipient_row["delivered_at"].isoformat(),
                }) 

    return dict(row)


# Get assigned users from a task
@db_error_handler
async def get_taskassignment(conn, task_id: int):
    query = """
        SELECT 
            ta.task_id,
            ta.user_id,
            u.profile_picture AS avatar,
            (u.first_name || ' ' || u.last_name) AS name        
        FROM task_assignments ta
        LEFT JOIN users u ON u.user_id = ta.user_id
        WHERE ta.task_id = $1 
        ORDER BY ta.task_id ASC;
    """
    rows = await conn.fetch(query, task_id)
    return [dict(row) for row in rows] if rows else None


# Unassign users from task
@db_error_handler
async def delete_taskassignment(conn, task_id: int, user_id: int):
    query = """
        DELETE FROM task_assignments
        WHERE task_id = $1 AND user_id = $2
        RETURNING *
    """
    row = await conn.fetchrow(query, task_id, user_id)
    
    if row:
        workspace_id = await conn.fetchval(
            "SELECT workspace_id from tasks WHERE task_id = $1",
            task_id
        )
        workspace_name = await conn.fetchval(
            "SELECT name FROM workspaces WHERE workspace_id = $1",
            workspace_id
        )
        notif_query = """
            INSERT INTO notifications (content, workspace_id)
            VALUES ($1, $2)
            RETURNING notification_id
        """
        notif_row = await conn.fetchrow(
            notif_query,
            f"You have been unassigned from Task {task_id}.",
            workspace_id
        )
        if notif_row:
            recipient_query = """
                INSERT INTO notification_recipients (notification_id, user_id, is_read)
                VALUES ($1, $2, FALSE)
                RETURNING recipient_id, user_id, is_read, delivered_at
            """
            recipient_row = await conn.fetchrow(
                recipient_query,
                notif_row["notification_id"],
                user_id
            )
            recipient_row = await conn.fetchrow(
                recipient_query,
                notif_row["notification_id"],
                user_id
            )
            await push_notifications(user_id, {
                "notification_id": notif_row["notification_id"],
                "user_id": user_id,
                "recipient_id": recipient_row["recipient_id"],
                "content": f"You have been removed from Task {task_id}",
                "workspace_name": workspace_name,
                "is_read": recipient_row["is_read"],
                "delivered_at": recipient_row["delivered_at"].isoformat(),
            })

    return dict(row) if row else None
