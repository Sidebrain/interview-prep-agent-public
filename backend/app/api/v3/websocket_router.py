import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.event_agents.connection_manager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()

logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, interview_session_id: str
) -> None:
    logger.info(
        f"Received search param on websocket sample: {interview_session_id}"
    )
    agent = await manager.connect(
        websocket=websocket, interview_session_id=interview_session_id
    )
    try:
        while True:
            await agent.channel.receive_message()

    except WebSocketDisconnect:
        await manager.disconnect(interview_session_id)
        print(f"Client #{interview_session_id} diconnected")
