from pydantic import BaseModel, Field
from app.event_agents.evaluations.evaluator_base import (
    EvaluatorSimple,
    EvaluatorStructured,
)


relevance_evaluator = EvaluatorSimple(
    evaluation_schema="check the relevance of the answer to the question"
)

exaggeration_evaluator = EvaluatorSimple(
    evaluation_schema="check the exaggeration of the answer"
)


class StructuredThinkingSchema(BaseModel):
    sample_framework: str = Field(
        description="a sample framework given the question "
    )
    user_framework: str = Field(
        description="the implicit framework the user has used in their answer to the question"
    )
    evaluation: str = Field(
        description="the evaluation of the user's framework against the sample framework"
    )


structured_thinking_evaluator = EvaluatorStructured(
    evaluation_schema=StructuredThinkingSchema
)
