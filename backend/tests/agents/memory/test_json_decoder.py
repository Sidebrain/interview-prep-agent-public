import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic.fields import FieldInfo

from app.event_agents.evaluations.evaluator_base import (
    EvaluatorSimple,
    EvaluatorStructured,
)
from app.event_agents.evaluations.evaluators import (
    exaggeration_evaluator,
    relevance_evaluator,
    structured_thinking_evaluator,
)
from app.event_agents.memory.config_builder import (
    AgentConfigJSONDecoder,
    ConfigBuilder,
)
from app.types.interview_concept_types import QuestionAndAnswer


@pytest.fixture
def sample_uuid() -> UUID:
    return UUID("9557ee35-dcf8-4849-b699-61c48698fc26")


@pytest.fixture
def sample_evaluator_config(sample_uuid: UUID) -> dict[str, Any]:
    with open(f"config/agent_{sample_uuid}.json", "r") as f:
        data: dict[str, Any] = json.load(f)
        return data


@pytest.fixture
def decoder() -> type[json.JSONDecoder]:
    return AgentConfigJSONDecoder


@pytest.fixture
def sample_evaluator_state() -> dict[str, Any]:
    return {
        "questions": [
            QuestionAndAnswer(
                question="Can you describe a project where you used PHP? What challenges did you face, and how did you overcome them?",
                sample_answer="In my previous role, I worked on a content management system built with PHP. One of the significant challenges was optimizing the performance as the number of users increased. I started by profiling the code to identify bottlenecks and implemented caching mechanisms using Redis, which improved load times significantly.",
                options="Answer should include a specific project, challenges faced, and methods used to overcome them.",
            ),
            QuestionAndAnswer(
                question="What PHP frameworks are you familiar with, and how have you applied them in your past projects?",
                sample_answer="I am familiar with Laravel and CodeIgniter. In one project, I used Laravel to build a RESTful API for a mobile application, which helped us streamline data interactions between the client and the server.",
                options="Answers could include frameworks like Laravel, Symfony, or CodeIgniter and examples of their application.",
            ),
        ],
        "evaluators": {
            "Exaggeration Evaluator": exaggeration_evaluator,
            "Relevance Evaluator": relevance_evaluator,
            "Structured Thinking Evaluator": structured_thinking_evaluator,
            "Rubric Evaluator": structured_thinking_evaluator,
        },
    }


class TestAgentConfigJSONDecoder:
    def test_questions_decoding(
        self,
        decoder: type[json.JSONDecoder],
        sample_evaluator_config: dict[str, Any],
    ) -> None:
        result = json.loads(
            json.dumps(sample_evaluator_config), cls=decoder
        )
        assert "questions" in result
        assert isinstance(result["questions"], list)
        assert all(
            isinstance(q, QuestionAndAnswer)
            for q in result["questions"]
        )

    def test_simple_evaluator_decoding(
        self,
        decoder: type[json.JSONDecoder],
        sample_evaluator_config: dict[str, Any],
    ) -> None:
        result = json.loads(
            json.dumps(sample_evaluator_config), cls=decoder
        )

        assert "evaluators" in result
        assert isinstance(result["evaluators"], dict)

        evaluator = result["evaluators"]["Exaggeration Evaluator"]
        assert isinstance(evaluator, EvaluatorSimple)
        assert (
            evaluator.evaluation_schema
            == "check the exaggeration of the answer"
        )

        assert isinstance(
            result["evaluators"]["Relevance Evaluator"], EvaluatorSimple
        )
        evaluator = result["evaluators"]["Relevance Evaluator"]
        assert (
            evaluator.evaluation_schema
            == "check the relevance of the answer to the question"
        )

    def test_structured_evaluator_decoding(
        self,
        decoder: type[json.JSONDecoder],
        sample_evaluator_config: dict[str, Any],
    ) -> None:
        result = json.loads(
            json.dumps(sample_evaluator_config), cls=decoder
        )

        assert "evaluators" in result
        evaluator = result["evaluators"][
            "Structured Thinking Evaluator"
        ]
        assert isinstance(evaluator, EvaluatorStructured)

        model = evaluator.evaluation_schema
        expected_fields = [
            "sample_framework",
            "user_framework",
            "evaluation",
        ]
        for field in expected_fields:
            assert field in model.model_fields

        assert (
            model.model_fields["sample_framework"].annotation
            == list[str]
        )
        assert (
            model.model_fields["user_framework"].annotation == list[str]
        )
        assert model.model_fields["evaluation"].annotation == list[str]

    def test_field_type_conversion(
        self, decoder: type[AgentConfigJSONDecoder]
    ) -> None:
        decoder_instance = decoder()
        test_schema = {"type": "array", "items": {"type": "string"}}

        field_type, field = decoder_instance._get_field_type(
            test_schema
        )
        assert field_type == list[str]
        assert isinstance(field, FieldInfo)


class TestConfigBuilder:
    # def test_save_and_load_state(
    #     self,
    #     sample_uuid: UUID,
    #     tmp_path: Path,
    #     sample_evaluator_config: dict[str, Any],
    # ) -> None:
    #     # Redirect config saves to temporary directory
    #     Path(tmp_path / "config").mkdir(exist_ok=True)

    #     # Save state
    #     with pytest.MonkeyPatch.context() as mp:
    #         mp.chdir(tmp_path)
    #         ConfigBuilder.save_state(
    #             sample_uuid, sample_evaluator_config
    #         )

    #         # Load state
    #         loaded_state = ConfigBuilder.load_state(sample_uuid)

    #         # Verify the loaded state
    #         assert "evaluator_config" in loaded_state
    #         assert "evaluators" in loaded_state["evaluator_config"]

    #         # Verify evaluators were properly decoded
    #         evaluators = loaded_state["evaluator_config"]["evaluators"]
    #         assert isinstance(
    #             evaluators["Exaggeration Evaluator"], EvaluatorSimple
    #         )
    #         assert isinstance(
    #             evaluators["Relevance Evaluator"], EvaluatorSimple
    #         )
    #         assert isinstance(
    #             evaluators["Rubric Evaluator"], EvaluatorStructured
    #         )
    #         assert isinstance(
    #             evaluators["Structured Thinking Evaluator"],
    #             EvaluatorStructured,
    #         )

    def test_load_state_nonexistent_file(self) -> None:
        # Test loading state from non-existent file
        sample_uuid = uuid4()
        loaded_state = ConfigBuilder.load_state(sample_uuid)
        assert loaded_state == {}

    def _verify_evaluator_schema(
        self,
        loaded_state: dict[str, Any],
        key: str,
        evaluator_to_check_against: EvaluatorSimple
        | EvaluatorStructured,
    ) -> None:
        evaluator = loaded_state["evaluators"].get(key)
        assert evaluator is not None
        assert isinstance(
            evaluator, EvaluatorSimple | EvaluatorStructured
        )

    def test_load_state_existing_file(
        self,
        sample_uuid: UUID,
    ) -> None:
        # Test loading state from existing file
        loaded_state = ConfigBuilder.load_state(sample_uuid)
        assert isinstance(loaded_state, dict)
        assert loaded_state.get("questions") is not None
        assert isinstance(loaded_state["questions"], list)
        assert all(
            isinstance(q, QuestionAndAnswer)
            for q in loaded_state["questions"]
        )
        assert loaded_state.get("evaluators") is not None
        assert isinstance(loaded_state["evaluators"], dict)
        self._verify_evaluator_schema(
            loaded_state,
            "Exaggeration Evaluator",
            exaggeration_evaluator,
        )
        self._verify_evaluator_schema(
            loaded_state, "Relevance Evaluator", relevance_evaluator
        )
        self._verify_evaluator_schema(
            loaded_state,
            "Structured Thinking Evaluator",
            structured_thinking_evaluator,
        )
        # self._verify_evaluator_schema(
        #     loaded_state, "Rubric Evaluator", structured_thinking_evaluator
        # )

    def test_save_state_create_file(
        self,
        sample_uuid: UUID,
        tmp_path: Path,
        sample_evaluator_state: dict[str, Any],
    ) -> None:
        # Test saving state creates file if it doesn't exist
        Path(tmp_path / "config").mkdir(exist_ok=True)

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            ConfigBuilder.save_state(
                sample_uuid, sample_evaluator_state
            )

            # Verify file exists
            config_file = Path(f"config/agent_{sample_uuid}.json")
            assert config_file.exists()

            # Verify file content is valid JSON and contains our data
            with open(config_file, "r") as f:
                saved_data = json.load(f)
                assert "questions" in saved_data
                assert isinstance(saved_data["questions"], list)

    # @pytest.mark.parametrize(
    #     "field_schema,expected_type",
    #     [
    #         ({"type": "string"}, str),
    #         ({"type": "integer"}, int),
    #         ({"type": "array", "items": {"type": "string"}}, list[str]),
    #         ({"type": "object"}, dict),
    #     ],
    # )
    # def test_field_type_mapping(
    #     self, field_schema, expected_type
    # ) -> None:
    #     decoder = AgentConfigJSONDecoder()
    #     assert decoder._get_field_type(field_schema) == expected_type
