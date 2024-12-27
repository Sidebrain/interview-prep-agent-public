import json
import logging
from pprint import PrettyPrinter
from typing import Any, Type

from pydantic import Field, create_model

from app.event_agents.evaluations.evaluator_base import (
    EvaluatorSimple,
    EvaluatorStructured,
)
from app.types.interview_concept_types import QuestionAndAnswer

logger = logging.getLogger(__name__)

pp = PrettyPrinter(indent=4, width=120, compact=True)


class AgentConfigJSONDecoder(json.JSONDecoder):
    def __init__(self) -> None:
        super().__init__(object_hook=self._object_hook)

    def _object_hook(self, dct: dict[str, Any]) -> dict[str, Any]:
        # convert the questions -> list[QuestionAndAnswer]
        if "questions" in dct:
            dct["questions"] = [
                QuestionAndAnswer.model_validate(q)
                for q in dct["questions"]
            ]
        # convert the evaluators -> list[Evaluator]

        if "evaluators" in dct:
            dct["evaluators"] = self._evaluator_builder(
                dct["evaluators"]
            )
        return dct

    def _get_field_type(
        self, field_schema: dict[str, Any]
    ) -> tuple[Type[Any], Any]:
        """Convert JSON schema types to Python types and create Pydantic Field with metadata

        Args:
            field_schema: The JSON schema field definition

        Returns:
            Tuple of (type, Field) for use with create_model
        """
        type_mapping: dict[str, type[Any]] = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        field_type = field_schema["type"]
        field_kwargs = {
            "description": field_schema.get("description", ""),
            "title": field_schema.get("title", None),
        }

        if field_type == "array":
            items = field_schema.get("items", {})
            if isinstance(items, dict):
                item_type = items.get("type", "string")
            else:
                item_type = "string"
            python_type = list[type_mapping.get(item_type, str)]  # type: ignore
        else:
            python_type = type_mapping.get(field_type, Any)  # type: ignore

        return python_type, Field(**field_kwargs)  # type: ignore

    def _evaluator_builder(
        self, dct: dict[str, Any]
    ) -> dict[str, EvaluatorSimple | EvaluatorStructured]:
        """Build evaluator instances from config dictionary

        Args:
            dct: Dictionary containing evaluator definitions

        Returns:
            Dictionary mapping evaluator names to instances
        """
        evaluators: dict[
            str, EvaluatorSimple | EvaluatorStructured
        ] = {}

        for evaluator_name, evaluator_schema in dct.items():
            if isinstance(evaluator_schema, dict):
                # Handle structured evaluator
                fields = {}
                required_fields = evaluator_schema.get("required", [])

                for field_name, field_schema in evaluator_schema[
                    "properties"
                ].items():
                    field_type, field = self._get_field_type(
                        field_schema
                    )

                    # Update field to mark as required if in required list
                    if field_name in required_fields:
                        field.default = ...

                    fields[field_name] = (field_type, field)

                model_name = evaluator_schema.get(
                    "title", "DynamicModel"
                )
                DynamicModel = create_model(
                    model_name,
                    **fields,
                )  # type: ignore

                evaluators[evaluator_name] = EvaluatorStructured(
                    DynamicModel
                )

            elif isinstance(evaluator_schema, str):
                # Handle simple evaluator
                evaluators[evaluator_name] = EvaluatorSimple(
                    evaluation_schema=evaluator_schema
                )

        logger.info(f"Built {len(evaluators)} evaluators")
        return evaluators
