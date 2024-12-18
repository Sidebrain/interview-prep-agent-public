import json
from uuid import UUID

from pydantic import BaseModel


async def save_state(
    agent_id: UUID, field: str, value: str | BaseModel | list[BaseModel]
) -> None:
    """Save the current state of the interview to long term memory."""
    try:
        with open(f"config/agent_{agent_id}.json", "r+") as f:
            content = f.read()
            data = json.loads(content) if content.strip() else {}
    except FileNotFoundError:
        data = {}

    if isinstance(value, BaseModel):
        data[field] = value.model_dump()
    elif isinstance(value, list):
        data[field] = [
            v.model_dump() for v in value if isinstance(v, BaseModel)
        ]
    else:
        data[field] = value

    with open(f"config/agent_{agent_id}.json", "w") as f:
        json.dump(data, f, indent=4)
