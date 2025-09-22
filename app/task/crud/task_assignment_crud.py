from ...utils.decorators import db_error_handler
from ...notifications.events import push_notifications
from ...recent_activity.crud import add_activity_db

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
        row = await conn.fetchrow(
            """
            SELECT w.workspace_id, w.name AS workspace_name
            FROM tasks t
            JOIN workspaces w ON t.workspace_id = w.workspace_id
            WHERE t.task_id = $1
            """,
            task_id
        )
        workspace_id = row["workspace_id"]
        workspace_name = row["workspace_name"]
        content = f"User {user_id} has been assigned to task {task_id}."
        await add_activity_db(conn, workspace_id, None, content)

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
        row = await conn.fetchrow(
            """
            SELECT w.workspace_id, w.name AS workspace_name
            FROM tasks t
            JOIN workspaces w ON t.workspace_id = w.workspace_id
            WHERE t.task_id = $1
            """,
            task_id
        )
        workspace_id = row["workspace_id"]
        workspace_name = row["workspace_name"]
        content = f"User {user_id} has been assigned to task {task_id}."
        await add_activity_db(conn, workspace_id, None, content)
        
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
