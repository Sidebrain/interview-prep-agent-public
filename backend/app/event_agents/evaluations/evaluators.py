from pydantic import BaseModel, Field

from app.event_agents.evaluations.evaluator_base import (
    EvaluatorSimple,
    EvaluatorStructured,
)

relevance_evaluator = EvaluatorSimple(
    evaluation_schema="what questions would you ask the user to check if the answer is relevant to the question?"
)

exaggeration_evaluator = EvaluatorSimple(
    evaluation_schema="what questions would you ask the user to check if they are exaggerating?"
)


class StructuredThinkingSchema(BaseModel):
    sample_framework: list[str] = Field(
        description="a sample framework given the question "
    )
    user_framework: list[str] = Field(
        description="the implicit framework the user has used in their answer to the question"
    )
    evaluation: list[str] = Field(
        description="the evaluation of the user's framework against the sample framework"
    )


structured_thinking_evaluator = EvaluatorStructured(
    evaluation_schema=StructuredThinkingSchema
)


# class CommunicationSchema(BaseModel):
#     dance: list[str] = Field(
#         description="Evaluation of the dance of the user's answer. The dance is the way the user establishes the interplay between conflict and resolution through content"
#     )
#     rhythm: list[str] = Field(
#         description="Evaluation of the rhythm of the user's answer. The rhythm is the way the user's answer flows from one point to another"
#     )
#     tone: list[str] = Field(
#         description="Evaluation of the tone of the user's answer. The tone is the way the user's answer is delivered. The more conversational the better"
#     )
#     direction: list[str] = Field(
#         description="Evaluation of how well the end of the answer is connected to the beginning, via the middle"
#     )
#     storylenses: list[str] = Field(
#         description="Evaluation of the storylenses of the user's answer. The storylenses is your unique viewpoint, your story, your lens vs regurgitation from memory"
#     )


# communication_evaluator = EvaluatorStructured(
#     evaluation_schema=CommunicationSchema
# )
