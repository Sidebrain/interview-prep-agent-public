from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

from app.types.websocket_types import WebsocketFrame

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, token: str):
        await websocket.accept()
        if token not in self.active_connections:
            self.active_connections[token] = websocket
        print(f"Client connected: {token}")

    def disconnect(self, token: str):
        if token in self.active_connections:
            del self.active_connections[token]

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def receive_message(self, websocket: WebSocket):
        message_from_client = await websocket.receive_text()
        print(f"Message received: {message_from_client}")
        match message_from_client:
            case "ping":
                await self.process_heartbeat(websocket)
            case _:
                await self.send_message(message_from_client, websocket)

    async def route_message(self, message: str, websocket: WebSocket):
        # send to the agent or the maanger agent that is responsible for the client
        print(f"Message received: {message}")
        print("Routing message to the appropriate handler")
        pass

    async def process_heartbeat(self, websocket: WebSocket):
        await self.send_message("pong", websocket)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid4())
    await manager.connect(websocket=websocket, token=client_id)
    try:
        while True:
            # data = await websocket.receive_text()
            await manager.receive_message(websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client #{client_id} diconnected")
