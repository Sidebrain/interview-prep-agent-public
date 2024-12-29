import asyncio
import logging
from collections import defaultdict
from typing import Awaitable, Callable, Type, TypeVar
from uuid import uuid4

from app.event_agents.orchestrator.events import BaseEvent
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)

Event = TypeVar("Event", bound=BaseEvent | WebsocketFrame)


class Broker:
    def __init__(self) -> None:
        self.session_id: str = str(uuid4())
        self._subscribers: dict[
            str, list[Callable[..., Awaitable[None]]]
        ] = defaultdict(list)
        self._event_queue: asyncio.Queue[BaseEvent | WebsocketFrame] = (
            asyncio.Queue()
        )
        self._is_running: bool = False
        self._process_events_task: asyncio.Task[None] | None = None

    async def subscribe(
        self,
        event_type: Type[Event],
        handler: Callable[..., Awaitable[None]],
    ) -> None:
        """
        Subscribe to an event type with a handler function.

        Args:
            event_type (BaseModel): The Pydantic model class representing the event type
            handler (callable): The async function to be called when the event occurs

        The handler will be invoked whenever an event of the specified type is published.
        """
        self._subscribers[event_type.__name__].append(handler)

    async def unsubscribe(
        self,
        event_type: Type[Event],
        handler: Callable[..., Awaitable[None]],
    ) -> None:
        """
        Unsubscribe from an event type with a handler function.

        Args:
            event_type (BaseModel): The Pydantic model class representing the event type
            handler (callable): The handler function to be removed from the subscription list

        Removes the specified handler from the list of subscribers for the given event type.
        """
        self._subscribers[event_type.__name__].remove(handler)

    async def publish(self, event: BaseEvent | WebsocketFrame) -> None:
        """
        Publish an event to the message queue.

        Args:
            event (dict): The event object to be published

        Adds the event to the asyncio Queue for processing by subscribed handlers.
        """
        await self._event_queue.put(event)

    async def _process_events(self) -> None:
        """
        Process events from the message queue.

        Continuously monitors the event queue while the broker is running.
        For each event:
        1. Retrieves the event type
        2. Finds all handlers subscribed to that event type
        3. Executes each handler with the event
        4. Also executes any handlers subscribed to all events ("*")
        """
        while self._is_running:
            event = await self._event_queue.get()
            event_type = event.__class__.__name__

            handlers = self._subscribers.get(event_type, [])
            handlers.extend(self._subscribers.get("*", []))

            # await asyncio.gather(*[handler(event) for handler in handlers])
            for handler in handlers:
                await handler(event)

    async def stop(self) -> None:
        """
        Stop the event processing loop.

        Terminates the event processing by:
        1. Setting the running flag to False
        2. Canceling the process events task if it exists
        """
        self._is_running = False
        if self._process_events_task:
            self._process_events_task.cancel()

    async def start(self) -> None:
        """
        Start the event processing loop.

        Initializes the event processing by:
        1. Setting the running flag to True
        2. Creating an asyncio task for the event processor
        Only starts if the broker is not already running.
        """
        if not self._is_running:
            self._is_running = True
            self._process_events_task = asyncio.create_task(
                self._process_events()
            )
