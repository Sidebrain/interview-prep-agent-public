from dataclasses import dataclass

from pydantic import BaseModel, Field


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
