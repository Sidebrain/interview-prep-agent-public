from typing import Dict

from fastapi import WebSocket


class Channel:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    def __post_init__(self):
        print("post init called")
        self.connect()

    async def send_message(self, message: str):
        await self.websocket.send_text(message)

    async def receive_message(self):
        message_from_client = await self.websocket.receive_text()
        print(f"Message received: {message_from_client}")
        match message_from_client:
            case "ping":
                await self.process_heartbeat()
            case _:
                await self.send_message(message_from_client)

    async def route_message(self, message: str):
        # send to the agent or the maanger agent that is responsible for the client
        print(f"Message received: {message}")
        print("Routing message to the appropriate handler")
        pass

    async def process_heartbeat(self):
        await self.send_message("pong")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Channel] = {}

    async def connect(self, websocket: WebSocket, token: str) -> Channel:
        await websocket.accept()
        if token not in self.active_connections:
            channel = Channel(websocket)
            self.active_connections[token] = channel
        print(f"Client connected: {token}")
        return channel

    def disconnect(self, token: str):
        if token in self.active_connections:
            del self.active_connections[token]
