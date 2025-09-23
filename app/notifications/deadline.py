import asyncpg 
from datetime import datetime, timedelta, timezone
from .events import push_notifications

async def send_deadline_reminders(pool: asyncpg.Pool):
    now = datetime.now(timezone.utc)
    async with pool.acquire() as conn:

        task_deadlines = await conn.fetch("""
            SELECT t.task_id, t.title, t.deadline, t.workspace_id, w.name AS workspace_name
            FROM tasks t
            JOIN workspaces w ON t.workspace_id = w.workspace_id
            WHERE t.status = 'pending'
            AND t.deadline IS NOT NULL
            AND t.deadline > $1
            """, now)
        
        workspace_deadlines = await conn.fetch("""
            SELECT w.due_date AS deadline, w.workspace_id, w.name AS workspace_name
            FROM workspaces w
            WHERE w.due_date IS NOT NULL
            AND w.due_date > $1                                                  
            """, now)
        

        for task in task_deadlines:
            deadline = task["deadline"]
            if isinstance(deadline, datetime) is False:
                deadline = datetime.combine(deadline, datetime.min.time(), tzinfo=timezone.utc)
        
            diff = deadline - now
            if diff <= timedelta(days=7):
                reminders = [timedelta(days=3), timedelta(hours=12), timedelta(hours=1)]
            elif diff > timedelta(days=30):
                reminders = [timedelta(days=7), timedelta(days=3), timedelta(hours=12), timedelta(hours=1)]
            else:
                reminders = []
            # reminders = [timedelta(minutes=0), timedelta(minutes=1), timedelta(minutes=5), timedelta(minutes=10)]

            for r in reminders:
                reminder_time = deadline - r
                if abs((reminder_time - now).total_seconds()) < 300:
                    content = f"[TASK] {task['title']} in {task['workspace_name']} → reminder at {reminder_time}"

                    notif_row = await conn.fetchrow("""
                        INSERT INTO notifications (content, workspace_id)
                        VALUES ($1, $2)
                        RETURNING notification_id, content
                    """, content, task["workspace_id"])

                    assinged_users = await conn.fetch(
                        "SELECT user_id FROM task_assignments WHERE task_id = $1",
                        task["task_id"]
                    )
                    for u in assinged_users:
                        recipient_row = await conn.fetchrow("""
                        INSERT INTO notification_recipients(notification_id, user_id, is_read)
                        VALUES ($1, $2, FALSE)
                        RETURNING recipient_id, user_id, is_read, delivered_at                     
                    """, notif_row["notification_id"], u["user_id"])
                        
                        await push_notifications(u["user_id"], {
                            "notification_id": notif_row["notification_id"],
                            "user_id": u["user_id"],
                            "recipient_id": recipient_row["recipient_id"],
                            "content": notif_row["content"],
                            "workspace_name": task["workspace_name"],
                            "is_read": recipient_row["is_read"],
                            "delivered_at": recipient_row["delivered_at"].isoformat(),
                        })

        for ws in workspace_deadlines:
            deadline = ws["deadline"]
            if isinstance(deadline, datetime) is False:
                deadline = datetime.combine(deadline, datetime.min.time(), tzinfo=timezone.utc)
           
            diff = deadline - now
            if diff <= timedelta(days=7):
                reminders = [timedelta(days=3), timedelta(hours=12), timedelta(hours=1)]
            elif diff > timedelta(days=30):
                reminders = [timedelta(days=7), timedelta(days=3), timedelta(hours=12), timedelta(hours=1)]
            else:
                reminders = []
            reminders = [timedelta(minutes=0), timedelta(minutes=1), timedelta(minutes=5), timedelta(minutes=10)]

            for r in reminders:
                reminder_time = deadline - r
                if abs((reminder_time - now).total_seconds()) < 300:
                    content = f"[WORKSPACE] {ws['workspace_name']} due → reminder at {reminder_time}"

                    notif_row = await conn.fetchrow("""
                        INSERT INTO notifications (content, workspace_id)
                        VALUES ($1, $2)
                        RETURNING notification_id, content
                    """, content, ws["workspace_id"])

                    members = await conn.fetch(
                        "SELECT user_id FROM workspace_members WHERE workspace_id = $1",
                        ws["workspace_id"]
                    )

                    for m in members:
                        recipient_row = await conn.fetchrow("""
                                INSERT INTO notification_recipients(notification_id, user_id, is_read)
                                VALUES ($1, $2, FALSE)
                                RETURNING recipient_id, user_id, is_read, delivered_at
                            """, notif_row["notification_id"], m["user_id"])
                        
                        await push_notifications(m["user_id"], {
                            "notification_id": notif_row["notification_id"],
                            "user_id": m["user_id"],
                            "recipient_id": recipient_row["recipient_id"],
                            "content": notif_row["content"],
                            "workspace_name": ws["workspace_name"],
                            "is_read": recipient_row["is_read"],
                            "delivered_at": recipient_row["delivered_at"].isoformat(),
                        })   
        
async def send_overdue_notifications(pool: asyncpg.pool):
    now = datetime.now(timezone.utc)
    async with pool.acquire() as conn:
        overdue_tasks = await conn.fetch("""
            SELECT t.task_id, t.title AS task_title, t.deadline AS task_deadline,
                   t.workspace_id, w.name AS workspace_name
            FROM tasks t
            JOIN workspaces w ON t.workspace_id = w.workspace_id
            WHERE t.status = 'pending'
            AND t.deadline IS NOT NULL
            AND t.deadline < $1
        """, now)

        for task in overdue_tasks:
            task_title = task["task_title"]
            task_deadline = task["task_deadline"]
            workspace_name = task["workspace_name"]

            content = f"TASK {task_title} in {workspace_name} is OVERDUE! (Deadline: {task_deadline})"

            notif_row = await conn.fetchrow("""
                INSERT INTO notifications (content, workspace_Id)
                VALUES ($1, $2)
                RETURNING notification_id, content
            """, content, task["workspace_id"])
            
            assigned_users = await conn.fetch(
                "SELECT user_id FROM task_assignments WHERE task_id = $1",
                task["task_id"]
            )
            
            for u in assigned_users:
                recipient_row = await conn.fetchrow("""
                    INSERT INTO notification_recipients(notification_id, user_id, is_read)
                    VALUES ($1, $2, FALSE)
                    RETURNING recipient_id, user_id, is_read, delivered_at
                """, notif_row["notification_id"], u["user_id"])
                
                await push_notifications(u["user_id"], {
                    "notification_id": notif_row["notification_id"],
                    "user_id": u["user_id"],
                    "recipient_id": recipient_row["recipient_id"],
                    "content": notif_row["content"],
                    "workspace_name": task["workspace_name"],
                    "is_read": recipient_row["is_read"],
                    "delivered_at": recipient_row["delivered_at"].isoformat(),
                })
