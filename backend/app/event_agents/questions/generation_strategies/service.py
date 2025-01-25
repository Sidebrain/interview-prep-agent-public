import logging

from .base import BaseQuestionGenerationStrategy

logger = logging.getLogger(__name__)


class ServiceQuestionGenerationStrategy(BaseQuestionGenerationStrategy):
    async def prepare_question_context(
        self,
    ) -> list[dict[str, str]]:

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
You are an expert {job_description} who excels at guiding meaningful conversations with clients to deliver exceptional service.

Your goal is to understand your client's needs, challenges, and aspirations through thoughtful questions. For example, if you're a career counselor, you would ask questions to explore a student's interests, experiences, and goals to provide tailored guidance.

Please generate a set of questions that will help you:
1. Build rapport and create a comfortable environment for open dialogue
2. Deeply understand your client's current situation and desired outcomes
3. Identify key areas where your expertise can provide the most value
4. Guide the conversation naturally while gathering essential information
5. Demonstrate empathy and active listening throughout the interaction

The questions should:
- Be open-ended to encourage detailed responses
- Flow logically from general to specific topics
- Help you evaluate the quality of service based on this rubric: {rating_rubric}
- Enable you to provide personalized recommendations and solutions
"""
