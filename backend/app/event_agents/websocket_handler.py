import logging
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import WebSocket

from app.event_agents.orchestrator.events import MessageReceivedEvent

if TYPE_CHECKING:
    from app.event_agents.orchestrator.broker import Broker

logger = logging.getLogger(__name__)


class Channel:
    def __init__(
        self,
        websocket: WebSocket,
        interview_id: UUID,
        broker: "Broker | None" = None,
    ) -> None:
        self.websocket = websocket
        self.broker = broker
        self.interview_id = interview_id

    def __repr__(self) -> str:
        return f"Channel(interview_id={self.interview_id})"

    async def send_message(self, message: str) -> None:
        await self.websocket.send_text(message)

    async def receive_message(self) -> str | None:
        message_from_client = await self.websocket.receive_text()
        match message_from_client:
            case "ping":
                await self.process_heartbeat()
                return None
            case _:
                event = MessageReceivedEvent(
                    message=message_from_client,
                    # TODO change this to interview_id in all events
                    session_id=self.interview_id,
                )
                logger.debug(
                    {
                        "event": "message_received",
                        "session_id": str(self.interview_id),
                        "message": message_from_client,
                    }
                )
                if not self.broker:
                    raise ValueError("Broker is not set")

                await self.broker.publish(event)
                return message_from_client

    async def route_message(self, message: str) -> None:
        # send to the agent or the maanger agent that is responsible for the client
        print(f"Message received: {message}")
        print("Routing message to the appropriate handler")
        pass

    async def process_heartbeat(self) -> None:
        await self.send_message("pong")
