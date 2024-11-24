import asyncio
from collections import defaultdict
import json
from typing import Callable
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.event_agents.evaluations.evaluators import (
    relevance_evaluator,
    exaggeration_evaluator,
    structured_thinking_evaluator,
)
from app.event_agents.orchestrator.interview_manager import (
    EvaluationManager,
    InterviewManager,
)
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.memory.factory import (
    create_memory_store,
)
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    MessageReceivedEvent,
    StartEvent,
)
from app.event_agents.websocket_handler import Channel

import logging

from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class Broker:
    def __init__(self):
        self.session_id: str = str(uuid4())
        self._subscribers: dict = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._is_running: bool = False

    async def subscribe(
        self, event_type: BaseModel, handler: Callable
    ):
        """
        Subscribe to an event type with a handler function.

        Args:
            event_type (BaseModel): The Pydantic model class representing the event type
            handler (callable): The async function to be called when the event occurs

        The handler will be invoked whenever an event of the specified type is published.
        """
        self._subscribers[event_type.__name__].append(
            handler
        )

    async def unsubscribe(
        self, event_type: BaseModel, handler: Callable
    ):
        """
        Unsubscribe from an event type with a handler function.

        Args:
            event_type (BaseModel): The Pydantic model class representing the event type
            handler (callable): The handler function to be removed from the subscription list

        Removes the specified handler from the list of subscribers for the given event type.
        """
        self._subscribers[event_type.__name__].remove(
            handler
        )

    async def publish(self, event: dict):
        """
        Publish an event to the message queue.

        Args:
            event (dict): The event object to be published

        Adds the event to the asyncio Queue for processing by subscribed handlers.
        """
        await self._event_queue.put(event)

    async def _process_events(self):
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

    async def stop(self):
        """
        Stop the event processing loop.

        Terminates the event processing by:
        1. Setting the running flag to False
        2. Canceling the process events task if it exists
        """
        self._is_running = False
        if self._process_events_task:
            self._process_events_task.cancel()

    async def start(self):
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


class Agent:
    def __init__(self, channel: Channel):
        self.agent_id: UUID = uuid4()
        self.session_id: UUID = uuid4()
        self.broker: Broker = Broker()
        self.channel = channel
        self.thinker = Thinker()
        self.memory_store = create_memory_store()
        self.evaluator = EvaluationManager(
            broker=self.broker,
            session_id=self.session_id,
            thinker=self.thinker,
            memory_store=self.memory_store,
            evaluators=[
                relevance_evaluator,
                exaggeration_evaluator,
                structured_thinking_evaluator,
            ],
        )
        self.interview_manager = InterviewManager(
            session_id=self.session_id,
            broker=self.broker,
            thinker=self.thinker,
            memory_store=self.memory_store,
            eval_manager=self.evaluator,
            max_time_allowed=10 * 60,  # 10 minutes
        )

    async def start(self):
        """
        Start the agent and initialize all components.

        1. Sets up all event subscribers
        2. Starts the event broker
        Must be called before the agent can process any events.
        """
        await self.setup_subscribers()
        await self.broker.start()

    async def setup_subscribers(self):
        """
        Initialize all event subscriptions for the agent.

        Subscribes to:
        - StartEvent: Handled by handle_start_event
        - MessageReceivedEvent: Handled by handle_message_received_event
        - AddToMemoryEvent: Handled by memory.add
        - WebsocketFrame: Handled by handle_websocket_frame
        Also sets up interview manager subscriptions.
        """
        await self.broker.subscribe(
            StartEvent, self.handle_start_event
        )
        await self.broker.subscribe(
            MessageReceivedEvent,
            self.handle_message_received_event,
        )
        # await self.broker.subscribe(
        #     AddToMemoryEvent,
        #     self.handle_add_to_memory_event,
        # )
        # await self.broker.subscribe(
        #     AddToMemoryEvent,
        #     self.interview_manager.handle_add_to_memory_event,
        # )
        await self.broker.subscribe(
            WebsocketFrame, self.handle_websocket_frame
        )
        await self.interview_manager.subscribe()

    async def handle_start_event(self, event: StartEvent):
        """
        Handle the initialization of a new interview session.

        Args:
            event (StartEvent): Event containing the session ID and initialization parameters

        Creates an async task for interview manager initialization to prevent blocking.
        Logs the start of the agent session.
        """
        try:
            logger.info(
                f"Starting agent {self.agent_id} for session {event.session_id}"
            )
            # doing this because otherwise the event loop is blocked
            # the status updates in the QuestionsGatheringEvent were not being published
            asyncio.create_task(
                self.interview_manager.initialize()
            )
        except Exception as e:
            logger.error(
                f"Error in handle_start_event: {str(e)}"
            )
            raise

    async def handle_message_received_event(
        self, event: MessageReceivedEvent
    ):
        """
        Process incoming messages from the websocket.

        Args:
            event (MessageReceivedEvent): Event containing the received message

        1. Validates and parses the message into a WebsocketFrame
        2. Creates and publishes an AddToMemoryEvent
        3. Triggers the next interview question

        Handles JSON decode errors and logs any processing errors.
        """
        try:
            message = event.message
            if message == None:
                return
            parsed_message = (
                WebsocketFrame.model_validate_json(
                    message, strict=False
                )
            )
            logger.info(
                f"Received message, parsed into websocket frame: {parsed_message}"
            )
            new_memory = AddToMemoryEvent(
                frame=parsed_message,
                session_id=self.session_id,
            )
            await self.broker.publish(new_memory)

            # From here on, the interview manager will take over
            # it will react to the AddToMemoryEvent and ask the next question
        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
        except Exception as e:
            logger.error(
                f"Error in handle_message_received_event: {str(e)}"
            )
            raise

    async def handle_websocket_frame(
        self, event: WebsocketFrame
    ):
        """
        Send a websocket frame to the client.

        Args:
            event (WebsocketFrame): The frame to be sent to the client

        Serializes the frame to JSON and sends it through the websocket channel.
        Logs any errors that occur during sending.
        """
        try:
            await self.channel.send_message(
                event.model_dump_json(by_alias=True)
            )
        except Exception as e:
            logger.error(
                f"Error in handle_websocket_frame: {str(e)}"
            )
            raise
