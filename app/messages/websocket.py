
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
from ..websocket_manager import ConnectionManager
from ..authentication.services import websocket_authentication
from ai_assistant.vectorstore.message_vector_store import ProcessMessageLogs
from .crud import insert_messages_to_db, insert_text_messages_to_db, get_sender_data, insert_message_attachments_db
from ..db_instance import db
from ..utils.logger import logger
from datetime import datetime, timezone
import json

router = APIRouter()
manager = ConnectionManager()
process = ProcessMessageLogs()

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
                "reply_to": payload["reply_to"],
                "is_pinned": False 
            }

            async with db.get_connection() as conn:
                async with conn.transaction():

                    if await manager.not_in_collection(f"{workspace_id}-{user_id}"):
                        sender_payload = await get_sender_data(user_id, workspace_id, conn)
                        sender_cache = await manager.store_cache(f"{workspace_id}-{user_id}", sender_payload)
                    else:
                        sender_cache = await manager.get_user_cache(f"{workspace_id}-{user_id}")

                    message_id = await insert_messages_to_db(message_data, conn)
                    await process.insert_data(workspace_id, message_id, payload.get("content"))
                    if payload["type"] == "text":
                        await insert_text_messages_to_db(text_data={"message_id": message_id, "content":payload["content"]["text"]}, conn=conn)

                    if payload["type"] == "attachment":
                        attachment_payload = payload["content"]
                        attachment_payload["message_id"] = message_id
                        await insert_message_attachments_db(attachment_payload, conn)
                        del payload["content"]["message_id"]


            message_obj = {
                "message_id": message_id,
                "workspace_id": workspace_id,
                "sender_id": user_id,
                "avatar": sender_cache["avatar"],
                "nickname": sender_cache["nickname"],
                "type": payload["type"],
                "content": payload.get("content"),
                "reply_to": payload.get("reply_to"),
                "sent_at": datetime.now(timezone.utc).isoformat()
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

