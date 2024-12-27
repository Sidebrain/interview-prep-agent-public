import json
import logging
from pprint import PrettyPrinter
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.event_agents.evaluations.evaluator_base import (
    EvaluatorSimple,
    EvaluatorStructured,
)

logger = logging.getLogger(__name__)

pp = PrettyPrinter(indent=4, width=120, compact=True)


class AgentConfigJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        # Handle Pydantic BaseModel
        if isinstance(obj, BaseModel):
            return obj.model_dump()

        # Handle lists/iterables of BaseModels
        if isinstance(obj, (list, tuple, set)):
            return [
                item.model_dump()
                if isinstance(item, BaseModel)
                else item
                for item in obj
            ]

        # Handle UUID objects
        if isinstance(obj, UUID):
            return str(obj)

        # Handle Evaluator objects
        if isinstance(obj, (EvaluatorSimple, EvaluatorStructured)):
            return obj.save_object()

        return super().default(obj)
