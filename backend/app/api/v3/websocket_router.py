from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.event_agents.connection_manager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    client_id = str(uuid4())
    agent = await manager.connect(websocket=websocket, token=client_id)
    try:
        while True:
            await agent.channel.receive_message()

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
        # agent.cleanup()
        print(f"Client #{client_id} diconnected")
