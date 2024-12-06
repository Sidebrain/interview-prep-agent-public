import asyncio
import logging
import json
import math

from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from app.agents.dispatcher import Dispatcher
from app.event_agents.evaluations.manager import (
    EvaluationManager,
)
from app.event_agents.interview.event_handler import InterviewEventHandler
from app.event_agents.interview.question_manager import QuestionManager
from app.event_agents.interview.time_manager import TimeManager
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    AskQuestionEvent,
    InterviewEndEvent,
    InterviewEndReason,
    QuestionsGatheringEvent,
    Status,
)

from app.types.interview_concept_types import (
    QuestionAndAnswer,
)

if TYPE_CHECKING:
    from app.event_agents.orchestrator.thinker import (
        Thinker,
    )
    from app.event_agents.orchestrator.broker import Broker
    from app.event_agents.memory.protocols import (
        MemoryStore,
    )
logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(
        self,
        session_id: UUID,
        broker: "Broker",
        thinker: "Thinker",
        memory_store: "MemoryStore",
        eval_manager: EvaluationManager,
        max_time_allowed: int | None = None,
    ):
        self.broker = broker
        self.thinker = thinker
        self.session_id = session_id
        self.max_time_allowed = (
            max_time_allowed if max_time_allowed else 2 * 60
        )  # 2 minutes default
        self.time_manager = TimeManager(
            broker, session_id, self.max_time_allowed
        )
        self.interview_event_handler = InterviewEventHandler(broker, session_id)
        self.question_manager = QuestionManager(thinker)
        self.eval_manager = eval_manager
        self.memory_store = memory_store

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "InterviewManager",
                "session": self.session_id.hex[:8],
                "time_remaining": self.max_time_allowed
                - self.time_manager.time_elapsed,
                "questions_remaining": len(self.question_manager.questions),
                "current_question": (
                    self.question_manager.current_question.question[:30] + "..."
                    if self.question_manager.current_question
                    else None
                ),
            },
            indent=2,
        )

    async def subscribe(self) -> None:
        """
        Subscribe to interview-related events.

        Subscribes to:
        - QuestionsGatheringEvent
        - AskQuestionEvent
        - InterviewEndEvent
        """
        logger.debug(
            "Subscribing to questions gathering event for session %s",
            self.session_id,
        )
        await self.broker.subscribe(
            QuestionsGatheringEvent,
            self.interview_event_handler.handle_questions_gathering_event,
        )
        await self.broker.subscribe(
            AskQuestionEvent,
            self.interview_event_handler.handle_ask_question,
        )
        await self.broker.subscribe(
            InterviewEndEvent,
            self.interview_event_handler.handle_interview_end,
        )
        await self.broker.subscribe(
            AddToMemoryEvent,
            self.handle_add_to_memory_event,
        )

    async def handle_add_to_memory_event(
        self, new_memory_event: AddToMemoryEvent
    ) -> None:
        """Handle new memory event and trigger next question."""
        logger.info(
            "Processing answer",
            extra={
                "manager": self,
                "answer_length": (
                    len(new_memory_event.frame.frame.content)
                    if new_memory_event.frame.frame.content
                    else 0
                ),
            },
        )

        try:
            await self.memory_store.add(new_memory_event.frame)
            evaluations = await self.eval_manager.handle_evaluation(
                questions=[self.question_manager.current_question]
            )
            logger.info(
                "Answer processed",
                extra={
                    "manager": self,
                    "evaluation_count": len(evaluations),
                },
            )

            for evaluation in evaluations:
                await self.broker.publish(evaluation)
            await self.ask_next_question()
        except Exception as e:
            logger.error(
                "Answer processing failed",
                extra={
                    "manager": self,
                    "error": str(e),
                },
            )
            raise

    async def initialize(self) -> list[QuestionAndAnswer]:
        """
        Initialize the interview session and start the question gathering process.

        This method:
        1. Publishes initial questions gathering event
        2. Gathers questions using the question manager
        3. Publishes completion event
        4. Starts the interview timer
        5. Initiates the first question

        Returns:
            list[QuestionAndAnswer]: List of gathered questions for the interview
        """
        logger.info("Starting new interview session: %s", self)

        # # Gather questions
        # questions = (
        #     await self.question_manager.gather_questions()
        # )
        # logger.info(
        #     "Questions gathered: %s",
        #     {
        #         "session": self.session_id.hex[:8],
        #         "question_count": len(questions),
        #     },
        # )

        # First event
        in_progress_event = QuestionsGatheringEvent(
            status=Status.in_progress,
            session_id=self.session_id,
        )

        await self.broker.publish(in_progress_event)

        # gather questions and store them in the instance variable
        questions = await self.question_manager.gather_questions()

        logger.info(
            "Questions gathered",
            extra={
                "session": self.session_id.hex[:8],
                "question_count": len(questions),
            },
        )

        # Second event
        completed_question_gathering_event = QuestionsGatheringEvent(
            status=Status.completed,
            session_id=self.session_id,
        )

        await self.broker.publish(completed_question_gathering_event)
        logger.debug(
            "\033[33m\nCompleted gathering %d questions. Published event.\n\033[0m",
            len(self.question_manager.questions),
        )

        # Start time tracking in the background# Start timer
        asyncio.create_task(self.time_manager.start_timer())
        logger.info("Timer started: %s", self.time_manager)

        time_unit = "seconds" if self.max_time_allowed < 60 else "minutes"
        time_to_answer = (
            self.max_time_allowed
            if self.max_time_allowed < 60
            else math.ceil(self.max_time_allowed / 60)
        )

        let_user_know_timer_started_event = Dispatcher.package_and_transform_to_webframe(
            f"Timer started. You have {time_to_answer} {time_unit} to answer the questions.",
            "content",
            frame_id=str(uuid4()),
        )
        await self.broker.publish(let_user_know_timer_started_event)

        # Start asking questions
        try:
            await self.ask_next_question()
        except Exception as e:
            logger.error(
                "Failed to ask first question",
                extra={
                    "session_id": self.session_id,
                    "manager_state": repr(self),
                    "error": str(e),
                },
                exc_info=True,
            )

        return questions

    async def ask_next_question(self) -> None:
        """Request and publish next question."""
        next_question = await self.question_manager.get_next_question()

        if next_question is None:
            logger.info("Interview complete: %s", self)
            interview_end_event = InterviewEndEvent(
                reason=InterviewEndReason.questions_exhausted,
                session_id=self.session_id,
            )
            await self.broker.publish(interview_end_event)
        else:
            logger.info("Asking question: %s", self.question_manager)
            await self.broker.publish(
                AskQuestionEvent(
                    question=next_question,
                    session_id=self.session_id,
                )
            )
