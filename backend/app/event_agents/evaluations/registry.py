import logging
from typing import Any

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
from app.event_agents.memory.config_builder import (
    ConfigBuilder,
)
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.types import AgentContext

logger = logging.getLogger(__name__)


class EvaluatorRegistry:
    def __init__(self, agent_context: "AgentContext") -> None:
        self.agent_context = agent_context
        self._evaluators: dict[str, EvaluatorBase[Any]] = {}
        self._thinker: Thinker = agent_context.thinker
        self.agent_id = agent_context.agent_id

    async def initialize(self) -> None:
        if self.are_evaluations_gathered_in_memory():
            evaluations_loaded_successfully = (
                self.load_evaluations_from_memory()
            )

            if evaluations_loaded_successfully:
                return
        else:
            logger.info("Initializing evaluator registry")
            await self.add_default_async_evaluators()
            self.add_default_sync_evaluators()
            logger.info(
                "Initialized evaluator registry",
            )
            self.save_state()

    def are_evaluations_gathered_in_memory(self) -> bool:
        try:
            return "evaluators" in ConfigBuilder.load_state(
                self.agent_id
            )
        except FileNotFoundError:
            return False

    def load_evaluations_from_memory(self) -> bool:
        loaded_state = ConfigBuilder.load_state(self.agent_id)
        if "evaluators" in loaded_state:
            self._evaluators = loaded_state["evaluators"]
            return True
        else:
            logger.info("No evaluators found in memory")
            return False

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

    def save_state(self) -> None:
        ConfigBuilder.save_state(
            self.agent_context.agent_id,
            {"evaluators": self._evaluators},
        )

    #         data = {}

    #     # Update with new evaluators
    #     data["evaluators"] = self._evaluators
    #     # Write the updated content
    #     with open(f"config/agent_{self.agent_id}.json", "w") as f:
    #         json.dump(data, f, cls=AgentConfigJSONEncoder, indent=4)
