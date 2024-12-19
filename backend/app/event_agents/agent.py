import asyncio
import json
import logging
import traceback
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.event_agents.interview.manager import InterviewManager
from app.event_agents.memory.factory import (
    create_memory_store,
)
from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.broker import Broker
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    MessageReceivedEvent,
    StartEvent,
)
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.types import AgentContext
from app.event_agents.websocket_handler import Channel
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)

#! locking this agent id to the config file
# AGENT_ID = UUID("3fe4ab11-64a1-4666-bcc7-c0dd7e55cdad")


@dataclass
class Agent:
    agent_id: UUID
    session_id: UUID
    broker: Broker
    thinker: Thinker
    channel: Channel
    is_active: bool
    memory_store: MemoryStore

    def __post_init__(self) -> None:
        self.interview_manager = InterviewManager(
            agent_context=self.context,
            max_time_allowed=10 * 60,  # 10 minutes
        )

    @classmethod
    def create(cls, channel: Channel) -> "Agent":
        return cls(
            agent_id=uuid4(),
            session_id=uuid4(),
            broker=Broker(),
            thinker=Thinker(),
            channel=channel,
            is_active=True,
            memory_store=create_memory_store(),
        )

    @property
    def context(self) -> AgentContext:
        return AgentContext(
            agent_id=self.agent_id,
            session_id=self.session_id,
            broker=self.broker,
            thinker=self.thinker,
            memory_store=self.memory_store,
        )

    async def stop(self) -> None:
        """Stop the agent and clean up all resources."""
        logger.info("Stopping agent %s", self.agent_id)
        self.is_active = False
        await self.broker.stop()

    async def start(self) -> None:
        """
        Start the agent and initialize all components.

        1. Sets up all event subscribers
        2. Starts the event broker
        Must be called before the agent can process any events.
        """
        await self.setup_subscribers()
        await self.broker.start()

    async def setup_subscribers(self) -> None:
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
        await self.broker.subscribe(
            WebsocketFrame, self.handle_websocket_frame
        )
        await self.interview_manager.subscribe()

    async def handle_start_event(self, event: StartEvent) -> None:
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

    async def handle_message_received_event(
        self, event: MessageReceivedEvent
    ) -> None:
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
            if message is None:
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
            logger.error(
                f"Error in handle_message_received_event: {str(e)}"
            )
            raise

    async def handle_websocket_frame(
        self, event: WebsocketFrame
    ) -> None:
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
                f"Error in handle_websocket_frame: {str(e)}",
                extra={
                    "context": {
                        "event": event.model_dump(by_alias=True),
                        "agent_id": str(self.agent_id),
                        "session_id": str(self.session_id),
                        "traceback": traceback.format_exc(),
                    }
                },
            )
            # mark as inactive on error
            await self.stop()
            raise
