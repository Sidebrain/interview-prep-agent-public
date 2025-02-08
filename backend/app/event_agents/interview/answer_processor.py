import logging
import traceback

from app.event_agents.conversations.turn import Turn
from app.event_agents.conversations.utils import choose_probe_direction
from app.event_agents.orchestrator.commands import (
    GenerateEvaluationsCommand,
    GeneratePerspectivesCommand,
)
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
)
from app.event_agents.questions.manager import QuestionManager
from app.event_agents.types import InterviewContext

logger = logging.getLogger(__name__)


class AnswerProcessor:
    def __init__(
        self,
        interview_context: InterviewContext,
        question_manager: QuestionManager,
    ) -> None:
        self.interview_context = interview_context
        self.question_manager = question_manager

    async def handler(self, event: AddToMemoryEvent) -> None:
        """Process the answer."""
        try:
            await self._add_answer_to_memory(event)
            await self._issue_appropriate_command()
            self._add_answer_to_conversation_tree(event)
            await self.question_manager.ask_next_question()
        except Exception as e:
            logger.error(
                f"Error in handle_add_to_memory_event: {str(e)}"
            )
            raise

    def _add_answer_to_conversation_tree(
        self,
        event: AddToMemoryEvent,
    ) -> None:
        conv_turn = Turn(
            question=self.question_manager.current_question,
            answer=event.frame,
            parent=self.interview_context.conversation_tree.current_position,
        )
        direction = choose_probe_direction(
            depth_probability=0.5, breadth_probability=0.5
        )
        self.interview_context.conversation_tree.add_turn(
            new_turn=conv_turn,
            direction=direction,
        )

    async def _add_answer_to_memory(
        self, event: AddToMemoryEvent
    ) -> None:
        """Add the answer to memory."""
        await self.interview_context.memory_store.add(event.frame)

    async def _issue_appropriate_command(self) -> None:
        try:
            if self.question_manager.current_question is None:
                return
            # check if evaluations are enabled
            if self.interview_context.interview_abilities.evaluations_enabled:
                generate_evaluations_command = (
                    GenerateEvaluationsCommand(
                        questions=[
                            self.question_manager.current_question
                        ]
                    )
                )
                await self.interview_context.broker.publish(
                    generate_evaluations_command
                )

            # check if perspectives are enabled
            if self.interview_context.interview_abilities.perspectives_enabled:
                generate_perspectives_command = (
                    GeneratePerspectivesCommand(
                        questions=[
                            self.question_manager.current_question
                        ]
                    )
                )
                await self.interview_context.broker.publish(
                    generate_perspectives_command
                )
        except Exception as e:
            logger.error(
                f"Error in issue_appropriate_command: {str(e)}"
                f"traceback: {traceback.format_exc()}"
            )
            raise
