import json
import logging
from typing import Any
from uuid import UUID

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
    def __init__(self, agent_id: UUID) -> None:
        self._evaluators: dict[str, EvaluatorBase[Any]] = {}
        self._thinker: Thinker = Thinker()
        self.agent_id = agent_id

    async def initialize(self) -> None:
        logger.info("Initializing evaluator registry")
        await self.add_default_async_evaluators()
        self.add_default_sync_evaluators()
        logger.info(
            "Initialized evaluator registry",
        )
        await self.save_state()

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
            extra={
                "context": {"sync evaluators": len(self._evaluators)}
            },
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
            extra={
                "context": {"async evaluators": len(self._evaluators)}
            },
        )

    def get_evaluators(self) -> dict[str, EvaluatorBase[Any]]:
        return self._evaluators

    async def save_state(self) -> None:
        # First read the existing content
        try:
            with open(f"config/agent_{self.agent_id}.json", "r") as f:
                content = f.read()
                data = json.loads(content) if content.strip() else {}
        except FileNotFoundError:
            data = {}

        # Update with new evaluators
        data["evaluators"] = {
            k: v.save_object() for k, v in self._evaluators.items()
        }

        # Write the updated content
        with open(f"config/agent_{self.agent_id}.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
