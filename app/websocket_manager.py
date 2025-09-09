from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {} # -> List of websockets/sockets
        self.connected_user_payload: Dict[str, Dict] = {}
    
    async def connect(self, workspace_id: int, websocket: WebSocket, protocol=str):
        """
            this accepts new Websocket and associate it with its respective workspace_id.
        
            - If this is the first connection for the workspace, create a new list.
            - Then add this client's socket to that list.
            
            the moment a member turned online we will connect their websocket to the workspace_id so that they can recieve new messages

        """
        await websocket.accept(subprotocol=protocol)
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
    
    def disconnect(self, workspace_id: int, websocket: WebSocket):
        """
            The moment there a member goes offline they will be removed the membere's websocket on the list and if there's no more member
            active, it will delete workspace from the lists of sockets
        """
        if workspace_id in self.active_connections:
            self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]
    
    async def broadcast(self, workspace_id: int, message: dict):
        """
            when you call this function, it will broadcast the message to where the workspace it belongs to.

            it will loop until all of the members recieve the message
        """
        if workspace_id in self.active_connections:
            for conn in self.active_connections[workspace_id]:
                await conn.send_json(message)

    async def store_cache(self, id:str, payload:dict):
        self.connected_user_payload[id] = {
            "avatar": payload["profile_picture"],
            "nickname": payload["nickname"]
        }
        return self.connected_user_payload[id]

    async def get_user_cache(self, id:str):
        return self.connected_user_payload[id]

    async def not_in_collection(self, id: str):
        if id not in self.connected_user_payload:
            return True
        return False