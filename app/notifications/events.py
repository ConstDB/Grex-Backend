import asyncio
from typing import Dict

listeners: Dict[int, asyncio.Future] = {}

async def register_listener(user_id: int, timeout: float = 30.0):
    """
    Wait for a notification for a specific user, or timeout.
    """
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    listeners[user_id] = future

    try:
        # Wait until push_notifications resolves this future
        result = await asyncio.wait_for(future, timeout)
        return result
    except asyncio.TimeoutError:
        return []
    finally:
        listeners.pop(user_id, None)

async def push_notifications(user_id: int, notif: dict):
    """
    Push a notification to a specific user if they are listening.
    """
    if user_id in listeners:
        future = listeners[user_id]
        if not future.done():
            future.set_result([notif])   
