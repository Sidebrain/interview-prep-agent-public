import logging
from typing import Type, Any

from app.event_agents.evaluations.evaluator_base import (
    EvaluatorBase,
    EvaluatorStructured,
)
from app.event_agents.evaluations.evaluators import (
    exaggeration_evaluator,
    relevance_evaluator,
    structured_thinking_evaluator,
)
from app.event_agents.evaluations.rating_rubric_evaluator import (
    RatingRubricEvaluationBuilder,
)
from app.event_agents.orchestrator.thinker import Thinker

logger = logging.getLogger(__name__)


class EvaluatorRegistry:
    def __init__(self) -> None:
        self._evaluators: dict[str, EvaluatorBase[Any]] = {}
        self._thinker: Thinker = Thinker()

    async def initialize(self) -> None:
        logger.info("Initializing evaluator registry")
        await self.add_default_async_evaluators()
        self.add_default_sync_evaluators()
        logger.info(
            "Initialized evaluator registry",
            extra={"context": {"evaluators": self._evaluators}},
        )

    def add_default_sync_evaluators(self) -> None:
        self._evaluators.update(
            {
                "Relevance Evaluator": relevance_evaluator,
                "Exaggeration Evaluator": exaggeration_evaluator,
                "Structured Thinking Evaluator": structured_thinking_evaluator,
            }
        )
        logger.info(
            "Added default sync evaluators",
            extra={"context": {"evaluators": self._evaluators}},
        )

    async def add_default_async_evaluators(self) -> None:
        schema_builder = RatingRubricEvaluationBuilder()
        structured_evaluation_schema = (
            await schema_builder.get_rating_evaluation_schema()
        )
        evaluator = EvaluatorStructured(structured_evaluation_schema)
        self._evaluators.update({"Rubric Evaluator": evaluator})
        logger.info(
            "Added default async evaluators",
            extra={"context": {"evaluators": self._evaluators}},
        )

    def get_evaluators(self) -> dict[str, EvaluatorBase[Any]]:
        return self._evaluators
