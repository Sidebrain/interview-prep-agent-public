from typing import Dict, List
from unittest.mock import MagicMock, mock_open, patch

import pytest

from app.event_agents.ranking.ranker import Ranker


@pytest.fixture
def mock_interviews() -> List[Dict[str, str]]:
    return [
        {"interview1.txt": "Sample interview content 1"},
        {"interview2.txt": "Sample interview content 2"},
    ]


@pytest.fixture
def ranker() -> Ranker:
    return Ranker()


@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open)
def test_load_interviews(
    mock_file: MagicMock, mock_listdir: MagicMock
) -> None:
    # Arrange
    mock_listdir.return_value = ["interview1.txt", "interview2.txt"]
    mock_file.return_value.read.side_effect = [
        "Sample interview content 1",
        "Sample interview content 2",
    ]

    # Act
    ranker = Ranker()

    # Assert
    assert len(ranker.interviews) == 2
    assert "interview1.txt" in ranker.interviews[0]
    assert "interview2.txt" in ranker.interviews[1]
    mock_listdir.assert_called_once_with("config/interviews")


@pytest.mark.asyncio
async def test_rank_returns_empty_list() -> None:
    # Arrange
    ranker = Ranker()
    test_interviews: List[Dict[str, str | int]] = [
        {"id": 1, "content": "Test interview 1"},
        {"id": 2, "content": "Test interview 2"},
    ]

    # Act
    result = await ranker.rank(test_interviews)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0
