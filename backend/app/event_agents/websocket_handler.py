from typing import TYPE_CHECKING

from fastapi import WebSocket


if TYPE_CHECKING:
    from app.event_agents.orchestrator.broker import Agent


class Channel:
    def __init__(self, websocket: WebSocket, agent: "Agent" = None):
        self.websocket = websocket
        self.agent = agent

    async def send_message(self, message: str):
        await self.websocket.send_text(message)

    async def receive_message(self) -> str | None:
        message_from_client = await self.websocket.receive_text()
        match message_from_client:
            case "ping":
                await self.process_heartbeat()
                return None
            case _:
                #! TODO: I dont know why i am sending the message back to the client
                await self.send_message(message_from_client)
                return message_from_client

    async def route_message(self, message: str):
        # send to the agent or the maanger agent that is responsible for the client
        print(f"Message received: {message}")
        print("Routing message to the appropriate handler")
        pass

    async def process_heartbeat(self):
        await self.send_message("pong")
