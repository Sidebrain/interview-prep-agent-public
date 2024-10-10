from typing import Optional
from pydantic import BaseModel, Field


class InterviewAgentConfig(BaseModel):
    role: str = Field(
        description="the role, or a description of the role, that is being hired for"
    )
    company_name: str = Field(
        description="the company, or a description of the company that is hiring for the role"
    )
    team_name: Optional[str] = Field(description="the team that is hiring for the role")
    internal_requirements: Optional[str] = Field(
        description="internal reuirements, cannot be shared with candidate, only for internal rating rubric generation",
    )
