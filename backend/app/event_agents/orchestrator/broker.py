import asyncio
from collections import defaultdict
import json
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.event_agents.orchestrator.interview_manager import InterviewManager
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.memory.factory import create_memory_store
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    AskQuestionEvent,
    InterviewEndEvent,
    InterviewEndReason,
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

            # await asyncio.gather(*[handler(event) for handler in handlers])
            for handler in handlers:
                logger.debug(f"Running handler: {handler} for event: {event_type}")
                await handler(event)
                logger.debug(
                    f"Finished running handler: {handler} for event: {event_type}"
                )

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
        self.interview_manager = InterviewManager(
            broker=self.broker, thinker=self.thinker, session_id=self.session_id
        )

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
        await self.broker.subscribe(WebsocketFrame, self.handle_websocket_frame)
        await self.interview_manager.subscribe()

    async def handle_start_event(self, event: StartEvent):
        """
        Here you would gather the questions from the Question list
        """
        try:
            logger.info(
                f"Starting agent {self.agent_id} for session {event.session_id}"
            )
            # doing this because otherwise the event loop is blocked
            # the status updates in the QuestionsGatheringEvent were not being published
            asyncio.create_task(self.interview_manager.initialize())
        except Exception as e:
            logger.error(f"Error in handle_start_event: {str(e)}")
            raise

    async def handle_message_received_event(self, event: MessageReceivedEvent):
        """
        Handle the message received event.
        """
        try:
            message = event.message
            if message == None:
                return
            parsed_message = WebsocketFrame.model_validate_json(message, strict=False)
            logger.info(
                f"Received message, parsed into websocket frame: {parsed_message}"
            )
            event = AddToMemoryEvent(
                frame=parsed_message,
                session_id=self.session_id,
            )
            await self.broker.publish(event)

            # ask the next question if there are any
            if self.interview_manager.questions:
                ask_question_event = AskQuestionEvent(
                    question=self.interview_manager.questions.pop(0),
                    session_id=self.session_id,
                )
                await self.broker.publish(ask_question_event)
            else:
                logger.info(f"No questions left to ask for session {self.session_id}")
                interview_end_event = InterviewEndEvent(
                    reason=InterviewEndReason.questions_exhausted,
                    session_id=self.session_id,
                )
                await self.broker.publish(interview_end_event)
        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
        except Exception as e:
            logger.error(f"Error in handle_message_received_event: {str(e)}")
            raise

    async def handle_websocket_frame(self, event: WebsocketFrame):
        """
        Handle the websocket frame.
        """
        try:
            logger.info(f"Sending websocket frame via channel")
            await self.channel.send_message(event.model_dump_json(by_alias=True))
        except Exception as e:
            logger.error(f"Error in handle_websocket_frame: {str(e)}")
            raise
