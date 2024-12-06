import asyncio
import json
from uuid import UUID, uuid4


from app.event_agents.evaluations.evaluators import (
    relevance_evaluator,
    exaggeration_evaluator,
    structured_thinking_evaluator,
    # communication_evaluator,
    # candidate_evaluation_evaluator,
)
from app.event_agents.evaluations.manager import EvaluationManager
from app.event_agents.interview.manager import InterviewManager
from app.event_agents.orchestrator.broker import Broker
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
                # communication_evaluator,
                # candidate_evaluation_evaluator,
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
        await self.broker.subscribe(StartEvent, self.handle_start_event)
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
        await self.broker.subscribe(WebsocketFrame, self.handle_websocket_frame)
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
            asyncio.create_task(self.interview_manager.initialize())
        except Exception as e:
            logger.error(f"Error in handle_start_event: {str(e)}")
            raise

    async def handle_message_received_event(self, event: MessageReceivedEvent):
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
            parsed_message = WebsocketFrame.model_validate_json(
                message, strict=False
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
            logger.error(f"Error in handle_message_received_event: {str(e)}")
            raise

    async def handle_websocket_frame(self, event: WebsocketFrame):
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
            logger.error(f"Error in handle_websocket_frame: {str(e)}")
            raise