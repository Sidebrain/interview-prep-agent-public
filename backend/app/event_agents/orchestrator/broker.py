import asyncio
from collections import defaultdict
import json
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.memory.factory import create_memory_store
from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    MessageReceivedEvent,
    StartEvent,
)
from app.event_agents.websocket_handler import Channel

import logging

from app.types.websocket_types import CompletionFrameChunk, WebsocketFrame

logger = logging.getLogger(__name__)


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
        self.thinker = Thinker()
        self.memory = create_memory_store()

    async def start(self):
        """
        Start the agent and subscribe to the start event.
        """
        await self.setup_subscribers()
        await self.broker.start()

    async def setup_subscribers(self):
        await self.broker.subscribe(StartEvent, self.handle_start_event)
        await self.broker.subscribe(
            MessageReceivedEvent, self.handle_message_received_event
        )
        await self.broker.subscribe(AddToMemoryEvent, self.memory.add)

    async def handle_start_event(self, event: StartEvent):
        """
        Handle the start event.
        """
        logger.info(f"Starting agent {self.agent_id} for session {event.session_id}")

        frame_id = str(uuid4())
        messages = self.memory.extract_memory_for_generation()
        response = await self.thinker.generate(messages=messages, debug=True)
        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            response, "content", frame_id
        )
        await self.channel.send_message(websocket_frame.model_dump_json(by_alias=True))

    async def handle_message_received_event(self, event: MessageReceivedEvent):
        """
        Handle the message received event.
        """
        message = event.message
        if message == None:
            return
        try:
            parsed_message = WebsocketFrame.model_validate_json(message, strict=False)
            logger.info(
                f"Received message, parsed into websocket frame: {parsed_message}"
            )
            event = AddToMemoryEvent(frame=parsed_message)
            await self.broker.publish(event)
        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
