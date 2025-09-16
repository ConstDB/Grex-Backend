import asyncio 
from typing import Dict

listeners: Dict[int, asyncio.Future] = {}

async def register_lister(user_id: int, timeout: float = 30.0):
    """
    Register a user to wait for notifications.
    """
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    listeners[user_id] = future

    try:
        result = await asyncio.wait_for(future, timeout-timeout)
        return result
    except asyncio.TimeoutError:
        return []
    finally:
        listeners.pop(user_id, None)

async def push_notifications(user_id: int, notif: dict):
    """
    Deliver a notification to a user if they are listening.
    """
    if user_id in listeners:
        future=listeners[user_id]
        if not future.done():
            future.set_result([notif])