import logging
from dataclasses import dataclass

from pydantic import BaseModel, Field

from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.schemas.mongo_schemas import (
    Interviewer,
)

# Create a logger instance
logger = logging.getLogger(__name__)


@dataclass
class RoleContext:
    system_prompt: str
    role_name: str


class StructuredRole(BaseModel):
    role_name: str = Field(
        description="The name of the role, eg Career Counselor, HR Manager, etc"
    )
    responsibilities: list[str] = Field(
        description="A list of responsibilities that the role requires"
    )
    qualifications: list[str] = Field(
        description="A list of qualifications that the role requires"
    )
    expertise: list[str] = Field(
        description="A list of expertise that the role requires"
    )
    personality: list[str] = Field(
        description="A list of personality traits that the role requires"
    )
    technical_skills: list[str] = Field(
        description="A list of technical skills that the role requires"
    )
    soft_skills: list[str] = Field(
        description="A list of soft skills that the role requires"
    )


class RoleBuilder:
    def __init__(self, interviewer: Interviewer) -> None:
        self.interviewer = interviewer
        self.system_prompt = None

    async def build(self, thinker: Thinker) -> RoleContext:
        structured_role = await self._analyze_job_description(thinker)
        prompt_instructions = self._create_prompt_instructions(
            structured_role
        )
        system_prompt = await self._generate_system_prompt(
            thinker, prompt_instructions
        )

        role_context = RoleContext(
            system_prompt=system_prompt,
            role_name=structured_role.role_name,
        )
        logger.info(
            "Role context generated",
            extra={
                "context": {
                    "structured_role": structured_role,
                    "role_context": role_context,
                }
            },
        )
        return role_context

    async def _analyze_job_description(
        self, thinker: Thinker
    ) -> StructuredRole:
        structured_role = await thinker.extract_structured_response(
            StructuredRole,
            messages=[
                {
                    "role": "user",
                    "content": self.interviewer.job_description,
                },
            ],
        )
        if not structured_role:
            logger.error("No structured role found")
            raise ValueError("No structured role found")
        return structured_role

    def _create_prompt_instructions(self, role: StructuredRole) -> str:
        return f"""
        Based on the following role analysis:
        
        Role: {role.role_name}
        Technical Skills: {', '.join(role.technical_skills)}
        Responsibilities: {', '.join(role.responsibilities)}
        Qualifications: {', '.join(role.qualifications)}
        Soft Skills: {', '.join(role.soft_skills)}
        Expertise Areas: {', '.join(role.expertise)}
        Key Personality Traits: {', '.join(role.personality)}
        
        Original Job Description:
        {self.interviewer.job_description}

        Write a system prompt that will help an AI agent embody and perform this professional role. The prompt should:
        1. Define the role's purpose and responsibilities
        2. Outline how to approach interactions with clients/users
        3. Describe how to apply the technical and soft skills in practice
        4. Explain how to demonstrate the personality traits through communication style
        
        The prompt should be written in second person ("you are...") and focus on guiding the AI to perform the role effectively.
        For example, a career counselor's prompt might begin with:
        "You are an experienced career counselor who helps individuals discover their ideal career paths. Your approach is to..."

        Make the prompt action-oriented and focused on service delivery, maintaining a professional and authentic voice throughout.
        """

    async def _generate_system_prompt(
        self, thinker: Thinker, instructions: str
    ) -> str:
        response = await thinker.generate(
            messages=[
                {"role": "user", "content": instructions},
            ],
        )
        if not response.choices[0].message.content:
            logger.error("No response from thinker")
            raise ValueError("No response from thinker")

        prompt = response.choices[0].message.content
        return prompt

    def persist(self) -> None:
        raise NotImplementedError
