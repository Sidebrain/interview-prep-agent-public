from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.connection_manager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid4())
    agent = await manager.connect(websocket=websocket, token=client_id)
    await agent.think()
    try:
        while True:
            # data = await websocket.receive_text()
            await agent.receive_message()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client #{client_id} diconnected")
