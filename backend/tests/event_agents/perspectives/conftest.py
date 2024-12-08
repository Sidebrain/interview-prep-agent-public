from unittest.mock import Mock
from app.event_agents.memory.factory import create_memory_store
from app.event_agents.memory.store import InMemoryStore
from app.types.websocket_types import WebsocketFrame


def create_mock_websocket_frames() -> list[Mock]:
    return [
        Mock(
            spec=WebsocketFrame,
            frame_id=f"frame-{i+1}",
            correlation_id=f"test-correlation-id-{address}-{i}",
            type=frame_type,
            address=address,
            frame=Mock(
                id=f"chunk-{i+1}",
                object=obj_type,
                model=model,
                role=role,
                content=f"Test content {i+1}",
                delta=delta,
                title=title,
                index=i,
                finish_reason=finish_reason,
            ),
        )
        for i, (
            frame_type,
            address,
            obj_type,
            role,
            delta,
            title,
            finish_reason,
            model,
        ) in enumerate(
            [
                (
                    "completion",
                    "content",
                    "chat.completion",
                    "assistant",
                    None,
                    None,
                    "stop",
                    "gpt-4",
                ),
                (
                    "streaming",
                    "thought",
                    "chat.completion.chunk",
                    "assistant",
                    "chunk",
                    "Thinking",
                    None,
                    "gpt-4",
                ),
                (
                    "input",
                    "human",
                    "human.completion",
                    "user",
                    None,
                    None,
                    "stop",
                    "infinity",
                ),
                (
                    "completion",
                    "evaluation",
                    "chat.completion",
                    "assistant",
                    None,
                    "Evaluation",
                    "stop",
                    "gpt-4",
                ),
                (
                    "input",
                    "human",
                    "human.completion",
                    "user",
                    None,
                    None,
                    "stop",
                    "infinity",
                ),
                (
                    "completion",
                    "perspective",
                    "chat.completion",
                    "assistant",
                    None,
                    "Perspective Analysis",
                    "stop",
                    "gpt-4",
                ),
            ]
        )
    ]


def create_test_memory_store(config_path: str | None = None) -> InMemoryStore:
    store = create_memory_store(config_path)
    store.memory = create_mock_websocket_frames()
    return store
