import asyncio
import logging
import math
from typing import Awaitable, Callable

from app.event_agents.evaluations.manager import EvaluationManager
from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.interview.time_manager import TimeManager
from app.event_agents.perspectives.manager import PerspectiveManager
from app.event_agents.questions.manager import QuestionManager
from app.event_agents.roles.manager import RoleBuilder
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import QuestionAndAnswer

logger = logging.getLogger(__name__)


class InterviewLifecyceManager:
    def __init__(
        self,
        interview_context: InterviewContext,
        question_manager: QuestionManager,
        time_manager: TimeManager,
        evaluation_manager: EvaluationManager,
        perspective_manager: PerspectiveManager,
        setup_subscribers: Callable[[], Awaitable[None]],
        setup_command_subscribers: Callable[[], Awaitable[None]],
    ) -> None:
        self.interview_context = interview_context
        self.question_manager = question_manager
        self.time_manager = time_manager
        self.evaluation_manager = evaluation_manager
        self.perspective_manager = perspective_manager
        self.setup_subscribers = setup_subscribers
        self.setup_command_subscribers = setup_command_subscribers

    async def stop(self) -> None:
        """Stop the interview manager and clean up all resources."""
        try:
            await self.interview_context.broker.stop()
            logger.info("Interview manager stopped and cleaned up")
        except Exception as e:
            logger.error(
                "Error in the cleanup process",
                extra={"error": str(e)},
                exc_info=True,
            )

    async def initialize(self) -> list[QuestionAndAnswer]:
        logger.info("Starting new interview session: %s", self)

        # originally part of start function of agent
        await self.setup_subscribers()
        await self.setup_command_subscribers()
        await self.interview_context.broker.start()

        await self.question_manager.initialize()

        timer_notification_string = await self.start_interview_timer()

        await NotificationManager.send_notification(
            self.interview_context.broker,
            timer_notification_string,
        )

        logger.info("Building role context")
        await RoleBuilder(self.interview_context.interviewer).build(
            self.interview_context.thinker
        )
        logger.info("Role context built")

        await self.initialize_evaluation_systems()
        await self.begin_questioning()

        return self.question_manager.questions

    async def start_interview_timer(self) -> str:
        """Start the interview timer and notify the user."""
        asyncio.create_task(self.time_manager.start_timer())
        logger.info("Timer started: %s", self.time_manager)

        time_unit = (
            "seconds"
            if self.interview_context.max_time_allowed < 60
            else "minutes"
        )
        time_to_answer = (
            self.interview_context.max_time_allowed
            if self.interview_context.max_time_allowed < 60
            else math.ceil(self.interview_context.max_time_allowed / 60)
        )

        timer_notification_string = f"Timer started. You have {time_to_answer} {time_unit} to answer the questions."
        return timer_notification_string

    async def initialize_evaluation_systems(self) -> None:
        """Initialize evaluation and perspective systems."""
        await self.evaluation_manager.evaluator_registry.initialize()
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
                    "interview_id": self.interview_context.interview_id,
                    "manager_state": repr(self),
                    "error": str(e),
                },
                exc_info=True,
            )
