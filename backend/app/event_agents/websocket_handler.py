import logging
from typing import TYPE_CHECKING

from fastapi import WebSocket

from app.event_agents.orchestrator.events import MessageReceivedEvent


if TYPE_CHECKING:
    from app.event_agents.orchestrator.broker import Agent


logger = logging.getLogger(__name__)


class Channel:
    def __init__(self, websocket: WebSocket, agent: "Agent" = None):
        self.websocket = websocket
        self.agent = agent

    def __repr__(self) -> str:
        return f"Channel(agent_id={self.agent.session_id if self.agent else None})"

    async def send_message(self, message: str):
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
                    session_id=self.agent.session_id,
                )
                logger.debug({
                    "event": "message_received",
                    "session_id": str(self.agent.session_id),
                    "message": message_from_client
                })
                await self.agent.broker.publish(event)
                return message_from_client

    async def route_message(self, message: str):
        # send to the agent or the maanger agent that is responsible for the client
        print(f"Message received: {message}")
        print("Routing message to the appropriate handler")
        pass

    async def process_heartbeat(self):
        await self.send_message("pong")
