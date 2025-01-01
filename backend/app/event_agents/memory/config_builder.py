import json
import logging
from pprint import PrettyPrinter
from typing import Any
from uuid import UUID

from app.event_agents.memory.json_decoders import AgentConfigJSONDecoder
from app.event_agents.memory.json_encoders import AgentConfigJSONEncoder

logger = logging.getLogger(__name__)

pp = PrettyPrinter(indent=4, width=120, compact=True)


class ConfigBuilder:
    @staticmethod
    def save_state(
        agent_id: UUID,
        dct: dict[str, Any],
    ) -> None:
        """Save the current state of the interview to long term memory."""
        try:
            with open(f"config/agent_{agent_id}.json", "r+") as f:
                content = f.read()
                data = json.loads(content) if content.strip() else {}
        except FileNotFoundError:
            data = {}

        # Add defensibility, only update non empty values
        for key, value in dct.items():
            if value or isinstance(
                value, (bool, int)
            ):  # allow explicit Falsy values
                data[key] = value

        with open(f"config/agent_{agent_id}.json", "w") as f:
            json.dump(data, f, cls=AgentConfigJSONEncoder, indent=4)

    @staticmethod
    def load_state(agent_id: UUID) -> Any:
        """Load the state of the interview from long term memory."""
        try:
            with open(f"config/agent_{agent_id}.json", "r") as f:
                return json.load(f, cls=AgentConfigJSONDecoder)
        except FileNotFoundError:
            return {}
