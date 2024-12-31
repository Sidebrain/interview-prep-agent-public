import asyncio
import json
import logging
import math
import traceback
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.evaluations.manager import EvaluationManager
from app.event_agents.evaluations.registry import EvaluatorRegistry
from app.event_agents.event_handlers import (
    MessageEventHandler,
    WebsocketEventHandler,
)
from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.interview.question_manager import QuestionManager
from app.event_agents.interview.time_manager import TimeManager
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    AskQuestionEvent,
    ErrorEvent,
    MessageReceivedEvent,
)
from app.event_agents.perspectives.manager import PerspectiveManager
from app.event_agents.perspectives.registry import PerspectiveRegistry
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(
        self,
        interview_context: "InterviewContext",
        max_time_allowed: int | None = None,
    ) -> None:
        # from the parent agent
        self.interview_context = interview_context
        self.agent_id = interview_context.agent_id
        self.broker = interview_context.broker
        self.channel = interview_context.channel
        self.thinker = interview_context.thinker
        self.interview_id = interview_context.interview_id
        self.memory_store = interview_context.memory_store

        self.max_time_allowed = (
            max_time_allowed if max_time_allowed else 2 * 60
        )  # 2 minutes default
        self.time_manager = TimeManager(
            broker=self.broker,
            max_time_allowed=self.max_time_allowed,
        )
        self.question_manager = QuestionManager(
            interview_context=self.interview_context,
        )
        self.eval_manager = EvaluationManager(
            interview_context=self.interview_context,
            evaluator_registry=EvaluatorRegistry(
                interview_context=self.interview_context
            ),
        )
        self.perspective_manager = PerspectiveManager(
            interview_context=self.interview_context,
            perspective_registry=PerspectiveRegistry(
                interview_context=self.interview_context
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
        await self.broker.subscribe(ErrorEvent, self.handle_error_event)

        await self.broker.subscribe(
            MessageReceivedEvent,
            MessageEventHandler(
                interview_context=self.interview_context
            ).handle_message_received_event,
        )

        await self.broker.subscribe(
            WebsocketFrame,
            WebsocketEventHandler(
                interview_context=self.interview_context
            ).handle_websocket_frame,
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

    async def handle_error_event(self, event: ErrorEvent) -> None:
        """Handle an error event."""
        logger.info(
            "Error event. Stopping interview manager.",
            extra={"context": {"error": event.error}},
        )
        await self.stop()

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
        await self.broker.stop()

    async def initialize(self) -> list[QuestionAndAnswer]:
        logger.info("Starting new interview session: %s", self)

        # originally part of start function of agent
        await self.setup_subscribers()
        await self.broker.start()

        await self.question_manager.initialize()

        timer_notification_string = await self.start_interview_timer()

        await NotificationManager.send_notification(
            self.interview_context.broker,
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
            self.interview_context.broker,
            "Evaluator registry initialized.",
        )

        await self.perspective_manager.perspective_registry.initialize()
        await NotificationManager.send_notification(
            self.interview_context.broker,
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
                self.interview_context.broker,
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
