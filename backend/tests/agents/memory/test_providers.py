import pytest
from app.agents.memory.providers import YAMLConfigProvider, PubSubMessagePublisher
from app.types.websocket_types import CompletionFrameChunk, WebsocketFrame
from .conftest import MockConfigProvider, MockMessagePublisher


def test_mock_config_provider_matches_real_behavior():
    # Create both real and mock providers
    real_provider = YAMLConfigProvider("config/agent_v2.yaml")
    mock_provider = MockConfigProvider()

    # Verify both return the same structure
    real_result = real_provider.get_system_prompt()
    mock_result = mock_provider.get_system_prompt()

    assert isinstance(real_result, list)
    assert isinstance(mock_result, list)
    assert all(isinstance(item, dict) for item in real_result)
    assert all(isinstance(item, dict) for item in mock_result)
    assert all("role" in item and "content" in item for item in real_result)
    assert all("role" in item and "content" in item for item in mock_result)


def test_mock_publisher_matches_real_behavior():
    real_publisher = PubSubMessagePublisher()
    mock_publisher = MockMessagePublisher()

    # Test that both handle the same input types
    test_frame = WebsocketFrame(
        # Create a test frame
        frame_id="test_id",
        type="completion",
        address="content",
        frame=CompletionFrameChunk(
            id="chunk_id",
            object="chat.completion",
            model="gpt-4",
            role="assistant",
            content="test content",
            delta=None,
            finish_reason="stop",
        ),
    )

    # Both should accept the same parameters without raising exceptions
    real_publisher.publish("test_topic", test_frame)
    mock_publisher.publish("test_topic", test_frame)
