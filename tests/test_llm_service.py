import os
import pytest
from unittest.mock import patch, MagicMock

# Add src to path to allow imports
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from core.llm_service import LLMService


@pytest.fixture
def mock_env_api_key():
    """Fixture to mock the GOOGLE_API_KEY environment variable."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
        yield


@patch("core.llm_service.genai")
def test_llm_service_init(mock_genai, mock_env_api_key):
    """Test that the LLMService initializes correctly."""
    service = LLMService()
    mock_genai.configure.assert_called_once_with(api_key="test_key")
    mock_genai.GenerativeModel.assert_called_once_with(
        "gemini-2.5-flash-lite-preview-06-17"
    )
    assert service.model is not None


@patch("core.llm_service.genai")
def test_llm_service_generate_response(mock_genai, mock_env_api_key):
    """Test that generate_response returns the correct text."""
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Hello, world!"
    mock_genai.GenerativeModel.return_value = mock_model

    service = LLMService()
    response = service.generate_response("A prompt")

    mock_model.generate_content.assert_called_once_with("A prompt")
    assert response == "Hello, world!"


@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set")
def test_llm_service_integration():
    """Integration test to check actual API call. Skips if key is not set."""
    service = LLMService()
    response = service.generate_response("Say hello")
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\nIntegration test response: {response}")
