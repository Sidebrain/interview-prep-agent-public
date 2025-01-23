import logging

from .base import BaseQuestionGenerationStrategy

logger = logging.getLogger(__name__)


class ServiceQuestionGenerationStrategy(BaseQuestionGenerationStrategy):
    async def prepare_question_context(
        self,
    ) -> list[dict[str, str]]:
        # we need to generate a question bank for this behavior mode
        # this will take the job description and rating rubric
        # then the base class will take care of the rest

        job_description = (
            self.interview_context.interviewer.job_description
        )
        rating_rubric = self.interview_context.interviewer.rating_rubric

        instruction_prompt = self.build_templated_intruction_prompt(
            job_description, rating_rubric
        )

        response = await self.interview_context.thinker.generate(
            messages=[
                {
                    "role": "user",
                    "content": instruction_prompt,
                },
            ],
        )
        if response.choices[0].message.content is None:
            raise ValueError("No content in response")
        question_bank = response.choices[0].message.content

        #! TODO not the right place to be doing this, but ok for now refactor later
        self.interview_context.agent_profile.question_bank = question_bank
        await self.interview_context.agent_profile.save()

        return [
            {
                "role": "user",
                "content": question_bank,
            },
        ]

    def build_templated_intruction_prompt(
        self, job_description: str, rating_rubric: str
    ) -> str:
        return f"""
You are an expert at creating questions for delivering a service to a customer.
        
Description of the job that you are good at:
{job_description}

The rating rubric that you use to evaluate yourself:
{rating_rubric}

Your task is to generate a comprehensive set of questions that:
1. Allow you to deliver the service to the customer
2. Allows you to evaluate yourself based on the provided rating rubric
3. Focus on customer service, teamwork, and problem-solving scenarios
4. Are open-ended and encourage detailed responses
"""
