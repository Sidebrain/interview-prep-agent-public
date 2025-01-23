from .base import BaseQuestionGenerationStrategy


class InterviewQuestionGenerationStrategy(
    BaseQuestionGenerationStrategy
):
    async def prepare_question_context(
        self,
    ) -> list[dict[str, str]]:
        messages = [
            {
                "role": "user",
                "content": self.interview_context.interviewer.question_bank,
            },
        ]
        return messages
