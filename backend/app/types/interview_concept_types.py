from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Context(BaseModel):
    context: str = Field(
        ...,
        description="The context for the interview",
    )


class Concept(BaseModel):
    reward: Literal["excellent", "acceptable", "lacking"] = Field(
        ...,
        description="""A reward for the detail provided in the concept. Generally one would expect a reward of 'excellent' for a concept that is well thought out and detailed, 'acceptable' for a concept that is just complete but lacks details, and 'lacking' for a concept that is missing a lot of details.""",
    )


class Role(Concept):
    role: str = Field(
        ...,
        description="The role that the hiring manager is hiring for",
        title="Hiring role",
        max_length=100,
    )


class Designation(Concept):
    designation: str = Field(..., description="The official designation of the person ")


class Vision(Concept):
    vision: Optional[str] = Field(None, description="The vision of the company")


class Mission(Concept):
    mission: Optional[str] = Field(None, description="The mission of the company")


class Culture(Concept):
    culture: Optional[str] = Field(None, description="The culture of the company")


class Company(Concept):
    company_name: Optional[str] = Field(None, description="The name of the company")
    # vision: Optional[Vision]
    # mission: Optional[Mission]
    # culture: Optional[Culture]

    # @model_validator(mode="after")
    # def at_least_one_field_required(cls, values):
    #     if not any(
    #         values.get(field)
    #         for field in ["company_name", "vision", "mission", "culture"]
    #     ):
    #         raise ValueError(
    #             "At least one of company_name, vision, mission, or culture must be provided."
    #         )
    #     return values


class Requirement(Concept):
    requirement_details: str = Field(
        ...,
        description="Details like seniority, what they would we working on in the short and mid term, who they would be reporting to and who would be reporting to them, etc.",
    )


class Budget(Concept):
    budget: int = Field(..., description="The budget for the role")


class Expected(Concept):
    salary: int = Field(..., description="The expected salary for the role")


class Backup(Concept):
    backup_plan: str = Field(
        ...,
        description="The backup plan if the role is not filled or it turns out the candidate is not a good fit or the candidate performs poorly.",
    )


class CultureFit(Concept):
    culture_fit: str = Field(
        ...,
        description="The environment that the candidate would be working in. Details about the team, the company culture, and the work environment that are important to the candidate's success for the company as well as for themselves.",
    )


class InternalRequirements(Concept):
    internal_requirements: str = Field(
        ...,
        description="The internal requirements for the role. This could be the technical skills, soft skills, and other requirements that the candidate must meet in order to be successful in the role. A lot of these requirements will not make it to the job description, but are important for the hiring manager and the recruiter to know.",
    )


hiring_requirements = [
    Role,
    # Designation,
    # Company,
    # Requirement,
    # Budget,
    # # # Expected,
    # # Backup,
    # CultureFit,
    # InternalRequirements,
]


class QuestionAndAnswer(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    question: str = Field(
        ...,
        description="A question that the recruiter asks the hiring manager to get more information about the role",
        title="Interview question",
    )
    sample_answer: str = Field(
        ...,
        description="A sample answer using world knowledge and the context so far to answer the question. This is used to help the hiring manager have a good starting point that they can build on.",
        title="Expected answer",
    )
    options: str = Field(
        ...,
        description="Some options that the hiring manager can choose from",
        title="Correct answer",
    )


################################################################################
######################## Mock interview Types ##################################


class MockInterviewQuestion(BaseModel):
    question: str = Field(..., description="question to ask the candidate")
    rubric_params: list[str] = Field(
        ..., description="rubric params that the question is associated with"
    )
    sample_answer: list[str] = Field(
        ..., description="Possible sample answers to the question"
    )
    sample_answer_framework: list[str] = Field(
        ...,
        description="Possible frameworks for a good answer, this would be used to evaluate the structure that the candidate uses to answer the question",
    )


################################################################################


def main(): ...


if __name__ == "__main__":
    main()
