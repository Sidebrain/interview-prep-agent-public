import json
import logging

from app.event_agents.evaluations.manager import EvaluationManager
from app.event_agents.evaluations.registry import EvaluatorRegistry
from app.event_agents.interview.answer_processor import AnswerProcessor
from app.event_agents.interview.event_handlers import (
    AskQuestionEventHandler,
    EvaluationsGeneratedEventHandler,
    MessageEventHandler,
    PerspectiveGeneratedEventHandler,
    WebsocketMessageEventHandler,
)
from app.event_agents.interview.lifecycle_manager import (
    InterviewLifecyceManager,
)
from app.event_agents.interview.question_manager import QuestionManager
from app.event_agents.interview.time_manager import TimeManager
from app.event_agents.orchestrator.commands import (
    GenerateEvaluationsCommand,
    GeneratePerspectivesCommand,
)
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    AskQuestionEvent,
    ErrorEvent,
    EvaluationsGeneratedEvent,
    MessageReceivedEvent,
    PerspectivesGeneratedEvent,
)
from app.event_agents.perspectives.manager import PerspectiveManager
from app.event_agents.perspectives.registry import PerspectiveRegistry
from app.event_agents.types import InterviewContext
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(
        self,
        interview_context: "InterviewContext",
    ) -> None:
        # from the parent agent
        self.interview_context = interview_context
        self.agent_id = interview_context.agent_id
        self.broker = interview_context.broker
        self.channel = interview_context.channel
        self.thinker = interview_context.thinker
        self.interview_id = interview_context.interview_id
        self.memory_store = interview_context.memory_store

        self.max_time_allowed = interview_context.max_time_allowed

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
        self.lifecycle_manager = InterviewLifecyceManager(
            interview_context=self.interview_context,
            question_manager=self.question_manager,
            time_manager=self.time_manager,
            evaluation_manager=self.eval_manager,
            perspective_manager=self.perspective_manager,
            setup_subscribers=self.setup_subscribers,
            setup_command_subscribers=self.setup_command_subscribers,
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
            WebsocketMessageEventHandler(
                interview_context=self.interview_context
            ).handler,
        )

        await self.broker.subscribe(
            AddToMemoryEvent,
            AnswerProcessor(
                interview_context=self.interview_context,
                question_manager=self.question_manager,
            ).handler,
        )

        await self.broker.subscribe(
            AskQuestionEvent,
            AskQuestionEventHandler(
                interview_context=self.interview_context
            ).handler,
        )

        await self.broker.subscribe(
            EvaluationsGeneratedEvent,
            EvaluationsGeneratedEventHandler(
                interview_context=self.interview_context
            ).handler,
        )

        await self.broker.subscribe(
            PerspectivesGeneratedEvent,
            PerspectiveGeneratedEventHandler(
                interview_context=self.interview_context
            ).handler,
        )

    async def setup_command_subscribers(self) -> None:
        await self.broker.subscribe(
            GenerateEvaluationsCommand,
            self.eval_manager.handle_evaluation_command,
        )

        await self.broker.subscribe(
            GeneratePerspectivesCommand,
            self.perspective_manager.handle_perspective_command,
        )

    ######### ######## ######## ######## ######## ######## #######

    async def handle_error_event(self, event: ErrorEvent) -> None:
        """Handle an error event."""
        logger.info(
            "Error event. Stopping interview manager.",
            extra={"context": {"error": event.error}},
        )
        await self.lifecycle_manager.stop()

    ########## ########## ########## ########## ########## ########## ##########

    async def initialize(self) -> None:
        await self.lifecycle_manager.initialize()
