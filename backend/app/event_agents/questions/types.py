from pydantic import BaseModel

from app.types.interview_concept_types import QuestionAndAnswer


class Questions(BaseModel):
    questions: list[QuestionAndAnswer]
