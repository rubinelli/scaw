"""
Tests for the WardenOrchestrator.
"""

import pytest
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, LogEntry
from core.orchestrator import WardenOrchestrator

# In-memory SQLite for testing
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_llm_service():
    """Fixture for a mocked LLMService."""
    mock = Mock()
    mock.choose_tool.return_value = None
    mock.synthesize_narrative.return_value = "A narrative response."
    mock.generate_response.return_value = "A generic response."
    return mock


@pytest.fixture
def orchestrator(mock_llm_service, db_session):
    """Fixture for a WardenOrchestrator instance with a mocked LLM service."""
    return WardenOrchestrator(mock_llm_service, db_session)


def test_handle_input_no_tool_chosen(orchestrator, db_session):
    """Tests that a generic response is generated if the LLM doesn't choose a tool."""
    orchestrator.handle_player_input("Hello?", db_session)
    orchestrator.llm_service.choose_tool.assert_called_once()
    orchestrator.llm_service.generate_response.assert_called_once_with("Hello?")
    assert db_session.query(LogEntry).count() == 2


def test_handle_input_tool_succeeds(orchestrator, db_session):
    """Tests the happy path where a tool is chosen and executes successfully."""
    orchestrator.llm_service.choose_tool.return_value = {
        "name": "roll_dice",
        "arguments": {"dice_string": "1d6"},
    }

    orchestrator.handle_player_input("Roll a d6", db_session)

    orchestrator.llm_service.choose_tool.assert_called_once()
    orchestrator.llm_service.synthesize_narrative.assert_called_once()
    assert db_session.query(LogEntry).count() == 2
