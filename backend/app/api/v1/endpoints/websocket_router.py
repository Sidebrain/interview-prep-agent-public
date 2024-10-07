import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text(f"Echo: {data}")

            # Simulate some server-side events
            await asyncio.sleep(5)
            await websocket.send_text("Server: Periodic message")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Websocket error: {e}")
    finally:
        pass


@router.get("/")
async def root():
    return {"message": "WebSocket server is running. Connect to /ws endpoint."}
