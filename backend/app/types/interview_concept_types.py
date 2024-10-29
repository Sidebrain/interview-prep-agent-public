from typing import Optional, get_type_hints
from pydantic import BaseModel, Field, model_validator


class Concept(BaseModel):
    reward: bool = Field(
        ...,
        description="""A boolean value that indicates whether the answer provided by the hiring manager is detailed enough to be rewarded. Like or dislike, binary classification.""",
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


class HiringRequirements(BaseModel):
    role: Role
    designation: Designation
    company: Company
    requirement: Requirement
    budget: Budget
    expected: Expected
    backup: Backup
    culture_fit: CultureFit
    internal_requirements: InternalRequirements

    @model_validator(mode="after")
    def validate_role_and_designation(cls, values):
        if values.get("role").role != values.get("designation").designation:
            raise ValueError(
                "The role and designation must be the same. The role is the title of the job, and the designation is the official title of the person."
            )
        return values

    @model_validator(mode="after")
    def validate_expected_and_budget(cls, values):
        if values.get("expected").salary > values.get("budget").budget:
            raise ValueError("The expected salary cannot be greater than the budget.")
        return values

    @model_validator(mode="after")
    def validate_backup_and_culture_fit(cls, values):
        if values.get("backup").backup_plan == values.get("culture_fit").culture_fit:
            raise ValueError(
                "The backup plan and the culture fit cannot be the same. The backup plan is the plan in case the role is not filled or the candidate does not work out, and the culture fit is the environment that the candidate would be working in."
            )
        return values


def main():
    # hiring_requirements = HiringRequirements(
    #     role=Role(reward=True, role="Software Engineer"),
    #     designation=Designation(reward=True, designation="Software Engineer"),
    #     company=Company(reward=True, company_name="Company A"),
    #     requirement=Requirement(reward=True, requirement_details="Experience building a team"),
    #     budget=Budget(reward=True, budget=100000),
    #     expected=Expected(reward=True, salary=90000),
    #     backup=Backup(reward=True, backup_plan="Hire a contractor"),
    #     culture_fit=CultureFit(reward=True, culture_fit="Remote work"),
    #     internal_requirements=InternalRequirements(
    #         reward=True, internal_requirements="Python, Django, React"
    #     ),
    # )
    # print(hiring_requirements)
    # t = get_type_hints(HiringRequirements)
    # print(t)
    # for k, v in t.items():
    #     print(k)
    #     print(get_type_hints(v))
    #     print(v.model_fields)
    # print(*HiringRequirements.model_fields, sep='\n')
    for n, py_class in get_type_hints(HiringRequirements).items():
        for n, f in py_class.model_fields.items():
            if n not in ["reward"]:
                print(n, f.description, sep="     ")


if __name__ == "__main__":
    main()
