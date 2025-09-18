
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
from ..websocket_manager import ConnectionManager
from ..users.auth import get_current_user, websocket_authentication
from .crud import insert_messages_to_db, insert_text_messages_to_db, get_sender_data
from ..db_instance import db
from ..utils.logger import logger
from datetime import datetime
import json

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/workspace/{workspace_id}/{user_id}")
async def websocket_message_endpoint(websocket: WebSocket, workspace_id: int, user_id: int, token: str):

    if websocket_authentication(token.strip()) == None:
        await websocket.close(code=1008, reason="Invalid credentials.")
        return
    
    await manager.connect(workspace_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            sender_cache = {}
            
            message_data = {
                "workspace_id": workspace_id,
                "sender_id": user_id,
                "message_type": payload["type"],
                "reply_to": payload["reply_to"] 
            }

            async with db.get_connection() as conn:
                async with conn.transaction():

                    if await manager.not_in_collection(f"{workspace_id}-{user_id}"):
                        sender_payload = await get_sender_data(user_id, workspace_id, conn)
                        sender_cache = await manager.store_cache(f"{workspace_id}-{user_id}", sender_payload)
                    else:
                        sender_cache = await manager.get_user_cache(f"{workspace_id}-{user_id}")

                    message_id = await insert_messages_to_db(message_data, conn)
                    if payload["type"] == "text":
                        await insert_text_messages_to_db(text_data={"message_id": message_id, "content":payload["content"]}, conn=conn)
                        


            message_obj = {
                "message_id": message_id,
                "workspace_id": workspace_id,
                "sender_id": user_id,
                "avatar": sender_cache["avatar"],
                "nickname": sender_cache["nickname"],
                "type": payload["type"],
                "content": payload.get("content"),
                "reply_to": payload.get("reply_to"),
                "sent_at": datetime.utcnow().isoformat()
            }

            await manager.broadcast(workspace_id, message_obj)

    except WebSocketDisconnect as e:
        logger.info(f"User {user_id} disconnects from workspace {workspace_id}")
        manager.disconnect(workspace_id, websocket)
    except Exception as e:
        logger.info(f"Unexpected Error: {e}")
        manager.disconnect(workspace_id, websocket)
    finally:
        manager.disconnect(workspace_id, websocket)

