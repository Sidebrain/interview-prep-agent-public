import logging
from typing import Annotated

import yaml
from pydantic import BaseModel, Field, create_model

from app.event_agents.orchestrator.thinker import Thinker

logger = logging.getLogger(__name__)


class CandidateEvaluationCriteria(BaseModel):
    criteria: str = Field(
        description="The evaluation criteria for the candidate assessment"
    )
    description: str = Field(
        description="The detailed description of how to evaluate this criteria"
    )
    rating_scale: list[str] = Field(
        description="The 1-5 rating scale definitions for this criteria"
    )


class CandidateEvaluationRubric(BaseModel):
    ratings: list[CandidateEvaluationCriteria] = Field(
        description="The evaluation criteria for assessing job candidates"
    )


class RatingRubricEvaluationBuilder:
    def __init__(self) -> None:
        self.thinker = Thinker()
        self.yaml_path = "config/artifacts_v2.yaml"

    def get_rating_rubric_string_from_yaml(self) -> dict[str, str]:
        logger.info(
            "Loading rating rubric",
            extra={"context": {"yaml_path": self.yaml_path}},
        )
        with open(self.yaml_path, "r") as file:
            config = yaml.safe_load(file)
        try:
            rubric = config["rating rubric in table format"]
            logger.debug("Successfully loaded rating rubric")
            return rubric
        except KeyError:
            logger.error(
                "Rating rubric not found",
                extra={"context": {"yaml_path": self.yaml_path}},
            )
            raise ValueError(
                f"Rating rubric not found in {self.yaml_path}"
            )

    async def extract_structured_rating_rubric(
        self, rubric_string: str
    ) -> CandidateEvaluationRubric:
        logger.info("Extracting structured rating rubric")
        try:
            structured_rubric: CandidateEvaluationRubric = await self.thinker.extract_structured_response(
                debug=True,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting rating rubrics from job descriptions.",
                    },
                    {"role": "user", "content": rubric_string},
                ],
                pydantic_structure_to_extract=CandidateEvaluationRubric,
            )
            logger.debug(
                "Successfully extracted rubric",
                extra={
                    "context": {
                        "criteria_count": len(structured_rubric.ratings)
                    }
                },
            )
            return structured_rubric
        except Exception as e:
            logger.error(
                "Failed to extract structured rating rubric",
                extra={"context": {"error": str(e)}},
                exc_info=True,
            )
            raise ValueError(
                f"Failed to extract structured rating rubric: {str(e)}"
            )

    async def build_evaluation_pydantic_model(
        self, rubric: CandidateEvaluationRubric
    ) -> BaseModel:
        logger.info("Building evaluation Pydantic model")
        fields = {}
        for rating in rubric.ratings:
            field_name = (
                rating.criteria.strip().replace(" ", "_").lower()
            )
            fields[field_name] = Annotated[
                str, Field(description=rating.description)
            ]
            logger.debug(
                "Added field",
                extra={"context": {"criteria": rating.criteria}},
            )
        logger.info(
            "Added all fields",
            extra={
                "context": {
                    "field_count": len(fields),
                    "fields": str(
                        fields
                    ),  # Convert fields dict to string to ensure it's serializable
                }
            },
        )

        try:
            evaluation_pydantic_schema = create_model(
                "DynamicEvaluationModel", **fields
            )
            logger.info(
                "Successfully created evaluation model",
                extra={"context": {"field_count": len(fields)}},
            )
            return evaluation_pydantic_schema
        except Exception as e:
            logger.error(
                "Failed to create evaluation model",
                extra={"context": {"error": str(e)}},
                exc_info=True,
            )
            raise ValueError(
                f"Failed to create evaluation model: {str(e)}"
            )

    async def get_rating_evaluation_schema(self) -> BaseModel:
        evaluation_pydantic_schema = (
            await self.build_evaluation_pydantic_model(
                await self.extract_structured_rating_rubric(
                    self.get_rating_rubric_string_from_yaml()
                )
            )
        )

        return evaluation_pydantic_schema
