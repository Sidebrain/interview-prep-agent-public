import asyncio
import json
import logging
import math

from app.event_agents.evaluations.manager import EvaluationManager
from app.event_agents.evaluations.registry import EvaluatorRegistry
from app.event_agents.event_handlers import (
    AnswerProcessor,
    AskQuestionEventHandler,
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
            ).handler,
        )

        await self.broker.subscribe(
            WebsocketFrame,
            WebsocketEventHandler(
                interview_context=self.interview_context
            ).handler,
        )

        await self.broker.subscribe(
            AddToMemoryEvent,
            AnswerProcessor(
                interview_context=self.interview_context,
                question_manager=self.question_manager,
                evaluation_manager=self.eval_manager,
                perspective_manager=self.perspective_manager,
            ).handler,
        )

        await self.broker.subscribe(
            AskQuestionEvent,
            AskQuestionEventHandler(
                interview_context=self.interview_context
            ).handler,
        )

    ######### ######## ######## ######## ######## ######## #######

    async def handle_error_event(self, event: ErrorEvent) -> None:
        """Handle an error event."""
        logger.info(
            "Error event. Stopping interview manager.",
            extra={"context": {"error": event.error}},
        )
        await self.stop()

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
            await self.question_manager.ask_next_question()
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
