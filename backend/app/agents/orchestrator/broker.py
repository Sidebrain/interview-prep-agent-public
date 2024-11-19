import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    correlation_id: UUID = Field(default_factory=uuid4)  # to track related events


class StartEvent(BaseEvent):
    session_id: UUID = Field(default_factory=uuid4)


class Broker:
    def __init__(self):
        self.session_id: str = str(uuid4())
        self._subscribers: dict = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._is_running: bool = False

    async def subscribe(self, event_type: str, handler: callable):
        """
        Subscribe to an event type with a handler function.
        """
        self._subscribers[event_type].append(handler)

    async def unsubscribe(self, event_type: str, handler: callable):
        """
        Unsubscribe from an event type with a handler function.
        """
        self._subscribers[event_type].remove(handler)

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
            handlers.extend(self._subscribers.get("*", []))

            await asyncio.gather(*[handler(event) for handler in handlers])

    async def stop(self):
        """
        Stop the event processing loop.
        """
        self._is_running = False

    async def start(self):
        """
        Start the event processing loop.
        """
        if not self._is_running:
            self._is_running = True
            await self._process_events()


class Agent(BaseModel):
    agent_id: UUID = Field(default_factory=uuid4)
    session_id: UUID = Field(default_factory=uuid4)
    broker: Broker = Field(default_factory=lambda: Broker())

    async def start(self):
        await self.broker.start()
