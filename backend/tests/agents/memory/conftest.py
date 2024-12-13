from typing import Dict, List
import pytest

from app.event_agents.memory.protocols import ConfigProvider, MessagePublisher
from app.types.websocket_types import WebsocketFrame


class MockConfigProvider(ConfigProvider):
    def __init__(self, system_prompt: List[Dict[str, str]] = None):
        # Validate input format
        if system_prompt is not None:
            for prompt in system_prompt:
                if not isinstance(prompt, dict):
                    raise TypeError("System prompt must be a list of dictionaries")
                if "role" not in prompt or "content" not in prompt:
                    raise ValueError("Each prompt must have 'role' and 'content' keys")
                if not isinstance(prompt["role"], str) or not isinstance(prompt["content"], str):
                    raise TypeError("Role and content must be strings")

        self.system_prompt = system_prompt or [{"role": "system", "content": "Test prompt"}]

    def get_system_prompt(self) -> List[Dict[str, str]]:
        return self.system_prompt

        
class MockMessagePublisher(MessagePublisher):
    def __init__(self):
        self.published_messages = []

    def publish(self, topic: str, frame: WebsocketFrame) -> None:
        # Validate input types
        if not isinstance(topic, str):
            raise TypeError("Topic must be a string")
        if not isinstance(frame, WebsocketFrame):
            raise TypeError("Frame must be a WebsocketFrame instance")
        
        self.published_messages.append((topic, frame))

# Test fixtures for different scenarios
@pytest.fixture
def mock_config_provider():
    return MockConfigProvider()

@pytest.fixture
def mock_config_provider_with_custom_prompt():
    return MockConfigProvider([
        {"role": "system", "content": "Custom prompt"},
        {"role": "system", "content": "Additional instruction"}
    ])

@pytest.fixture
def mock_message_publisher():
    return MockMessagePublisher()

# Additional tests for the mocks themselves
def test_mock_config_provider_validation():
    # Test invalid prompt format
    with pytest.raises(TypeError):
        MockConfigProvider([{"role": "system", "content": 123}])  # Invalid content type
    
    with pytest.raises(ValueError):
        MockConfigProvider([{"invalid_key": "value"}])  # Missing required keys
    
    with pytest.raises(TypeError):
        MockConfigProvider("not a list")  # Invalid input type

def test_mock_message_publisher_validation():
    publisher = MockMessagePublisher()
    
    # Test invalid topic type
    with pytest.raises(TypeError):
        publisher.publish(123, WebsocketFrame(...))  # Invalid topic type
    
    # Test invalid frame type
    with pytest.raises(TypeError):
        publisher.publish("topic", "not a frame")  # Invalid frame type
