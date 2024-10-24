from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

from app.types.websocket_types import WebsocketFrame
from app.websocket_handler import ConnectionManager

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid4())
    channel = await manager.connect(websocket=websocket, token=client_id)
    try:
        while True:
            # data = await websocket.receive_text()
            await channel.receive_message()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client #{client_id} diconnected")
