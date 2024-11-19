import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.event_agents.websocket_handler import Channel

import logging

from app.types.websocket_types import CompletionFrameChunk, WebsocketFrame

logger = logging.getLogger(__name__)


class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    correlation_id: UUID = Field(default_factory=uuid4)  # to track related events


class StartEvent(BaseEvent):
    session_id: UUID
    client_id: UUID


class WebsocketMessageEvent(BaseEvent):
    frame: WebsocketFrame
    session_id: UUID
    client_id: UUID


class Broker:
    def __init__(self):
        self.session_id: str = str(uuid4())
        self._subscribers: dict = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._is_running: bool = False

    async def subscribe(self, event_type: BaseModel, handler: callable):
        """
        Subscribe to an event type with a handler function.
        """
        self._subscribers[event_type.__name__].append(handler)
        logger.info(f"subscribers: {self._subscribers}")

    async def unsubscribe(self, event_type: BaseModel, handler: callable):
        """
        Unsubscribe from an event type with a handler function.
        """
        self._subscribers[event_type.__name__].remove(handler)

    async def publish(self, event: dict):
        """
        Publish an event to the message queue.
        """
        await self._event_queue.put(event)

    async def _process_events(self):
        """
        Process events from the message queue.
        """
        while self._is_running:
            event = await self._event_queue.get()
            event_type = event.__class__.__name__

            handlers = self._subscribers.get(event_type, [])
            logger.info(f"handlers: {handlers}")
            handlers.extend(self._subscribers.get("*", []))
            logger.info(f"handlers including *: {handlers}")

            await asyncio.gather(*[handler(event) for handler in handlers])

    async def stop(self):
        """
        Stop the event processing loop.
        """
        self._is_running = False
        if self._process_events_task:
            self._process_events_task.cancel()

    async def start(self):
        """
        Start the event processing loop.
        """
        if not self._is_running:
            self._is_running = True
            self._process_events_task = asyncio.create_task(self._process_events())


class Agent:
    def __init__(self, channel: Channel):
        self.agent_id: UUID = uuid4()
        self.session_id: UUID = uuid4()
        self.broker: Broker = Broker()
        self.channel = channel

    async def start(self):
        """
        Start the agent and subscribe to the start event.
        """
        await self.broker.subscribe(StartEvent, self.handle_start_event)
        await self.broker.start()

    async def handle_start_event(self, event: StartEvent):
        """
        Handle the start event.
        """
        logger.info(f"Starting agent {self.agent_id} for session {event.session_id}")
        print(f"Starting agent {self.agent_id} for session {event.session_id}")
        frame_id = str(uuid4())
        completion_frame = CompletionFrameChunk(
            id=str(uuid4()),
            object="chat.completion",
            model="gpt-4-turbo",
            role="assistant",
            content="Hello! I'm your AI interviewer. I'll be asking you some questions to understand your qualifications better. Let's begin with your background.",
            delta=None,
            index=0,
            finish_reason="stop",
        )

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address="content",
            frame=completion_frame,
        )
        logger.info(
            f"Sending completion frame: {websocket_frame.model_dump_json(indent=4)}"
        )
        await self.channel.send_message(websocket_frame.model_dump_json(by_alias=True))

    async def receive_message(self):
        """
        Receive a message from the channel.
        """
        message = await self.channel.receive_message()
        print(f"Received message: {message}")
