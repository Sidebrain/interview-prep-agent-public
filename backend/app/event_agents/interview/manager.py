import asyncio
import json
import logging
import math
import traceback
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

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
from app.event_agents.memory.config_builder import save_state
from app.types.websocket_types import WebsocketFrame

if TYPE_CHECKING:
    from app.event_agents.memory.protocols import (
        MemoryStore,
    )
    from app.event_agents.orchestrator.broker import Broker
    from app.event_agents.orchestrator.thinker import (
        Thinker,
    )
logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(
        self,
        agent_id: UUID,
        session_id: UUID,
        broker: "Broker",
        thinker: "Thinker",
        memory_store: "MemoryStore",
        eval_manager: EvaluationManager,
        perspective_manager: PerspectiveManager,
        notification_manager: NotificationManager,
        max_time_allowed: int | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.broker = broker
        self.thinker = thinker
        self.session_id = session_id
        self.max_time_allowed = (
            max_time_allowed if max_time_allowed else 2 * 60
        )  # 2 minutes default
        self.time_manager = TimeManager(
            notification_manager, session_id, self.max_time_allowed
        )
        self.question_manager = QuestionManager(thinker)
        self.eval_manager = eval_manager
        self.perspective_manager = perspective_manager
        self.memory_store = memory_store
        self.notification_manager = notification_manager

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "InterviewManager",
                "session": self.session_id.hex[:8],
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

    async def subscribe(self) -> None:
        await self.broker.subscribe(
            AddToMemoryEvent,
            self.handle_add_to_memory_event,
        )
        await self.broker.subscribe(
            AskQuestionEvent,
            self.handle_ask_question_event,
        )

    ######## Interview End Summary #########

    async def _generate_summary(self) -> None:
        """
        Generate a summary of the interview.
        """
        interview = self.memory_store.extract_memory_for_generation(
            address_filter=["content", "thought"],
        )
        perspectives = self.memory_store.extract_memory_for_generation(
            address_filter=["perspective"],
        )
        evaluations = self.memory_store.extract_memory_for_generation(
            address_filter=["evaluation"],
        )
        context = interview + perspectives + evaluations

        context = context + [
            {
                "role": "user",
                "content": self.summary_instruction(),
            }
        ]
        logger.info(
            "Generating summary of interview",
            extra={
                "context_length": len(context),
                "session_id": self.session_id,
                "context": [c["content"][:30] + "..." for c in context],
            },
        )

        summary = await self.thinker.generate(context)
        frame = Dispatcher.package_and_transform_to_webframe(
            summary,
            "content",
            frame_id=str(uuid4()),
        )

        await self.broker.publish(frame)

    def summary_instruction(self) -> str:
        return "using the interview transcript, evaluations, and perspectives, generate an analysis of the interview."

    ######### ######## ######## ######## ######## ######## #######

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

    async def initialize(self) -> list[QuestionAndAnswer]:
        logger.info("Starting new interview session: %s", self)

        await self.notification_manager.send_notification(
            "Interview started. Gathering questions..."
        )
        questions = await self.collect_and_store_questions()

        await save_state(self.agent_id, "questions", questions)

        await self.notification_manager.send_notification(
            "Questions gathered. Starting interview timer..."
        )

        timer_notification_string = await self.start_interview_timer()

        await self.notification_manager.send_notification(
            timer_notification_string
        )

        await self.initialize_evaluation_systems()
        await self.begin_questioning()

        return questions

    async def collect_and_store_questions(
        self,
    ) -> list[QuestionAndAnswer]:
        """Gather and store interview questions."""
        questions = await self.question_manager.gather_questions()
        logger.info(
            "Questions gathered",
            extra={
                "session": self.session_id.hex[:8],
                "question_count": len(questions),
            },
        )
        return questions

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

    async def initialize_evaluation_systems(self) -> None:
        """Initialize evaluation and perspective systems."""
        await self.eval_manager.evaluator_registry.initialize()
        await self.notification_manager.send_notification(
            "Evaluator registry initialized."
        )

        await self.perspective_manager.perspective_registry.initialize()
        await self.notification_manager.send_notification(
            "Perspective registry initialized."
        )

    async def begin_questioning(self) -> None:
        """Start the question-asking process."""
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

    async def ask_next_question(self) -> None:
        """Request and publish next question."""
        next_question = await self.question_manager.get_next_question()

        if next_question is None:
            logger.info("Interview complete: %s", self)
            await self.notification_manager.send_notification(
                "Questions exhausted. Interview ended."
            )
        else:
            logger.info("Asking question: %s", self.question_manager)

            # add the question to memory
            #! this needs a CQRS
            await self.add_questions_to_memory(next_question)

            await self.broker.publish(
                AskQuestionEvent(
                    question=next_question,
                    session_id=self.session_id,
                )
            )

    async def handle_ask_question_event(
        self, event: AskQuestionEvent
    ) -> None:
        """Send the question to the user."""
        frame_id = str(uuid4())
        question_thought_frame = (
            Dispatcher.package_and_transform_to_webframe(
                event.question,
                "thought",
                frame_id=frame_id,
            )
        )
        question_frame = Dispatcher.package_and_transform_to_webframe(
            event.question.question,
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
            question.question,
            "content",
            frame_id=str(uuid4()),
        )
        await self.memory_store.add(question_frame)
