import asyncio
import json
import logging
import math
import traceback
from uuid import UUID, uuid4

from app.event_agents.evaluations.registry import EvaluatorRegistry
from app.event_agents.interview import (
    AddToMemoryEvent,
    AskQuestionEvent,
    Dispatcher,
    EvaluationManager,
    NotificationManager,
    PerspectiveManager,
    QuestionAndAnswer,
    QuestionManager,
    TimeManager,
)
from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.broker import Broker
from app.event_agents.orchestrator.events import (
    MessageReceivedEvent,
    StartEvent,
)
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.perspectives.registry import PerspectiveRegistry
from app.event_agents.types import AgentContext
from app.event_agents.websocket_handler import Channel
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(
        self,
        agent_context: "AgentContext",
        memory_store: MemoryStore,
        agent_id: UUID,
        channel: Channel,
        broker: Broker,
        thinker: Thinker,
        interview_id: UUID,  # drop in replacement for interview_id
        max_time_allowed: int | None = None,
    ) -> None:
        # from the parent agent
        self.agent_context = agent_context
        self.agent_id = agent_id
        self.broker = broker
        self.channel = channel
        self.thinker = thinker
        self.interview_id = interview_id
        self.memory_store = memory_store

        self.max_time_allowed = (
            max_time_allowed if max_time_allowed else 2 * 60
        )  # 2 minutes default
        self.time_manager = TimeManager(
            agent_context=self.agent_context,
            max_time_allowed=self.max_time_allowed,
        )
        self.question_manager = QuestionManager(
            agent_context=self.agent_context,
        )
        self.eval_manager = EvaluationManager(
            agent_context=self.agent_context,
            evaluator_registry=EvaluatorRegistry(
                agent_context=self.agent_context
            ),
        )
        self.perspective_manager = PerspectiveManager(
            agent_context=self.agent_context,
            perspective_registry=PerspectiveRegistry(
                agent_context=self.agent_context
            ),
        )

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "InterviewManager",
                "session": self.interview_id.hex[:8],
                "time_remaining": self.max_time_allowed
                - self.time_manager.time_elapsed,
                "questions_remaining": len(
                    self.question_manager.questions
                ),
                "current_question": (
                    self.question_manager.current_question.question[:30]
                    + "..."
                    if self.question_manager.current_question
                    else None
                ),
            },
            indent=2,
        )

    async def setup_subscribers(self) -> None:
        await self.broker.subscribe(StartEvent, self.handle_start_event)
        await self.broker.subscribe(
            MessageReceivedEvent,
            self.handle_message_received_event,
        )
        await self.broker.subscribe(
            WebsocketFrame,
            self.handle_websocket_frame,
        )
        await self.broker.subscribe(
            AddToMemoryEvent,
            self.handle_add_to_memory_event,
        )
        await self.broker.subscribe(
            AskQuestionEvent,
            self.handle_ask_question_event,
        )

    ######### ######## ######## ######## ######## ######## #######

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
                        "interview_id": str(self.interview_id),
                        "traceback": traceback.format_exc(),
                    }
                },
            )
            # mark as inactive on error
            await self.stop()
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
                interview_id=self.interview_id,
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

    async def handle_start_event(self, event: StartEvent) -> None:
        print(
            "\033[91m" + "initializing the intervew manager" + "\033[0m"
        )
        try:
            await self.initialize()
        except Exception as e:
            logger.error(
                "Error in handle_start_event",
                extra={
                    "context": {
                        "manager": self,
                        "error": str(e),
                        "stacktrace": traceback.format_exc(),
                    }
                },
            )
            raise

    async def handle_add_to_memory_event(
        self, new_memory_event: AddToMemoryEvent
    ) -> None:
        """
        Process a new answer, evaluate it, generate perspectives, and advance to next question.
        """
        logger.info(
            "Processing answer",
            extra={
                "manager": self,
                "answer_length": self._get_answer_length(
                    new_memory_event
                ),
            },
        )

        try:
            await self._process_answer(new_memory_event)
            await self._generate_evaluations_and_perspectives()
            await self.ask_next_question()
        except Exception as e:
            logger.error(
                "Answer processing failed",
                extra={
                    "context": {
                        "manager": self,
                        "error": str(e),
                        "stacktrace": traceback.format_exc(),
                    }
                },
            )
            raise

    async def _process_answer(
        self, new_memory_event: AddToMemoryEvent
    ) -> None:
        """Store the answer in memory."""
        await self.memory_store.add(new_memory_event.frame)

    async def _generate_evaluations_and_perspectives(self) -> None:
        """Generate and publish evaluations and perspectives for the current question."""
        evaluations, perspectives = await asyncio.gather(
            self._generate_evaluations(), self._generate_perspectives()
        )

        logger.info(
            "Answer processed",
            extra={
                "manager": self,
                "evaluation_count": len(evaluations),
                "perspective_count": len(perspectives),
            },
        )

        await self._publish_results(evaluations, perspectives)

    async def _generate_evaluations(self) -> list[WebsocketFrame]:
        """Generate evaluations for the current question."""
        if self.question_manager.current_question is None:
            return []
        evaluations = await self.eval_manager.handle_evaluation(
            questions=[self.question_manager.current_question]
        )
        logger.info(
            "Evaluations generated",
            extra={
                "context": {
                    # "manager": self,
                    "evaluation_count": len(evaluations),
                }
            },
        )
        return evaluations

    async def _generate_perspectives(self) -> list[WebsocketFrame]:
        """Generate perspectives for the current question."""
        if self.question_manager.current_question is None:
            return []
        perspectives = (
            await self.perspective_manager.handle_perspective(
                questions=[self.question_manager.current_question]
            )
        )
        logger.info(
            "Perspectives generated",
            extra={
                "context": {
                    "manager": self,
                    "perspective_count": len(perspectives),
                }
            },
        )
        return perspectives

    async def _publish_results(
        self,
        evaluations: list[WebsocketFrame],
        perspectives: list[WebsocketFrame],
    ) -> None:
        """Publish evaluations and perspectives to the broker."""
        for evaluation in evaluations:
            await self.broker.publish(evaluation)
        for perspective in perspectives:
            await self.broker.publish(perspective)

    def _get_answer_length(
        self, new_memory_event: AddToMemoryEvent
    ) -> int:
        """Calculate the length of the answer content."""
        return (
            len(new_memory_event.frame.frame.content)
            if new_memory_event.frame.frame.content
            else 0
        )

    ########## ########## ########## ########## ########## ########## ##########

    async def stop(self) -> None:
        """Stop the interview manager and clean up all resources."""
        logger.info("Stopping interview manager %s", self.interview_id)
        await self.broker.stop()

    async def initialize(self) -> list[QuestionAndAnswer]:
        logger.info("Starting new interview session: %s", self)

        # originally part of start function of agent
        await self.setup_subscribers()
        await self.broker.start()

        await self.question_manager.initialize()

        timer_notification_string = await self.start_interview_timer()

        await NotificationManager.send_notification(
            self.agent_context,
            timer_notification_string,
        )

        await self.initialize_evaluation_systems()
        await self.begin_questioning()

        self.save_state()

        return self.question_manager.questions

    async def start_interview_timer(self) -> str:
        """Start the interview timer and notify the user."""
        asyncio.create_task(self.time_manager.start_timer())
        logger.info("Timer started: %s", self.time_manager)

        time_unit = (
            "seconds" if self.max_time_allowed < 60 else "minutes"
        )
        time_to_answer = (
            self.max_time_allowed
            if self.max_time_allowed < 60
            else math.ceil(self.max_time_allowed / 60)
        )

        timer_notification_string = f"Timer started. You have {time_to_answer} {time_unit} to answer the questions."
        return timer_notification_string

    def save_state(self) -> None:
        self.question_manager.save_state()
        self.eval_manager.evaluator_registry.save_state()

    async def initialize_evaluation_systems(self) -> None:
        """Initialize evaluation and perspective systems."""
        await self.eval_manager.evaluator_registry.initialize()
        await NotificationManager.send_notification(
            self.agent_context,
            "Evaluator registry initialized.",
        )

        await self.perspective_manager.perspective_registry.initialize()
        await NotificationManager.send_notification(
            self.agent_context,
            "Perspective registry initialized.",
        )

    async def begin_questioning(self) -> None:
        """Start the question-asking process."""
        try:
            await self.ask_next_question()
        except Exception as e:
            logger.error(
                "Failed to ask first question",
                extra={
                    "interview_id": self.interview_id,
                    "manager_state": repr(self),
                    "error": str(e),
                },
                exc_info=True,
            )

    async def ask_next_question(self) -> None:
        """Request and publish next question."""
        next_question = await self.question_manager.get_next_question()

        if next_question is None:
            logger.info("Interview complete: %s", self)
            await NotificationManager.send_notification(
                self.agent_context,
                "Questions exhausted. Interview ended.",
            )
        else:
            logger.info("Asking question: %s", self.question_manager)

            # add the question to memory
            #! this needs a CQRS
            await self.add_questions_to_memory(next_question)

            await self.broker.publish(
                AskQuestionEvent(
                    question=next_question,
                    interview_id=self.interview_id,
                )
            )

    async def handle_ask_question_event(
        self, event: AskQuestionEvent
    ) -> None:
        """Send the question to the user."""
        frame_id = str(uuid4())
        question_thought_frame = (
            Dispatcher.package_and_transform_to_webframe(
                event.question,  # type: ignore
                "thought",
                frame_id=frame_id,
            )
        )
        question_frame = Dispatcher.package_and_transform_to_webframe(
            event.question.question,  # type: ignore
            "content",
            frame_id=frame_id,
        )
        await self.broker.publish(question_thought_frame)
        await self.broker.publish(question_frame)

    async def add_questions_to_memory(
        self, question: QuestionAndAnswer
    ) -> None:
        """Add questions to memory."""
        question_frame = Dispatcher.package_and_transform_to_webframe(
            question.question,  # type: ignore
            "content",
            frame_id=str(uuid4()),
        )
        await self.memory_store.add(question_frame)
