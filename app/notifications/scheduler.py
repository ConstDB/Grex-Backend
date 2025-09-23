from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.notifications.deadline import send_deadline_reminders, send_overdue_notifications
from app.db.database import Database  

async def start_scheduler(pool):
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        send_deadline_reminders,
        "interval",
        minutes=5,
        args=[pool]  
    ),
    scheduler.add_job(
        send_overdue_notifications,
        "interval",
        minutes=1,
        args=[pool]
    )

    scheduler.start()
