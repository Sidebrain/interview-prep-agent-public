from typing import List

from pydantic import BaseModel

from app.types.interview_concept_types import QuestionAndAnswer


class CommandBase(BaseModel):
    pass


class GenerateEvaluationCommand(CommandBase):
    questions: List[QuestionAndAnswer]
    pass


class GeneratePerspectiveCommand(CommandBase):
    questions: List[QuestionAndAnswer]
    pass
