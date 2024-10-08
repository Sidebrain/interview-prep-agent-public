from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agents.agents import BaseAgent
from app.types.websocket_types import WebSocketStreamResponse

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    agent = BaseAgent("What is the meaning of life", websocket)
    await agent.process_goal()  # this sends the goal response
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                send_text_body = WebSocketStreamResponse(
                    id=uuid4().int, type="heartbeat", content="pong"
                )
                await websocket.send_text(send_text_body.model_dump_json())
            else:
                await agent.process_message(data)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Websocket error: {e}")
    finally:
        pass


@router.get("/")
async def root():
    return {"message": "WebSocket server is running. Connect to /ws endpoint."}
