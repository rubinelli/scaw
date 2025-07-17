"""
Tests for the WardenOrchestrator.
"""

import pytest
from unittest.mock import Mock, patch
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
    # Patch the world_tools module during orchestrator instantiation
    with patch("core.orchestrator.world_tools") as mock_world_tools:
        # Mock a sample tool
        mock_world_tools.sample_tool = lambda arg: {
            "status": f"tool executed with {arg}"
        }
        # Create the orchestrator instance
        orch = WardenOrchestrator(mock_llm_service, db_session)
        # Now, the orchestrator's available_tools will be populated from the mock
        return orch


def test_handle_input_no_tool_chosen(orchestrator, db_session):
    """Tests that a generic response is generated if the LLM doesn't choose a tool."""
    orchestrator.handle_player_input("Hello?", db_session)
    orchestrator.llm_service.choose_tool.assert_called_once()
    orchestrator.llm_service.generate_response.assert_called_once_with("Hello?")
    assert db_session.query(LogEntry).count() == 2  # Player + Warden


def test_handle_input_tool_succeeds(orchestrator, db_session):
    """Tests the happy path where a tool is chosen and executes successfully."""
    orchestrator.llm_service.choose_tool.return_value = {
        "name": "sample_tool",
        "arguments": {"arg": "test_value"},
    }

    orchestrator.handle_player_input("Use the sample tool.", db_session)

    orchestrator.llm_service.choose_tool.assert_called_once()
    orchestrator.llm_service.synthesize_narrative.assert_called_once()
    # Check that the narrative was synthesized with the correct tool result
    call_args, _ = orchestrator.llm_service.synthesize_narrative.call_args
    assert call_args[1] == "sample_tool"
    assert call_args[2] == {"status": "tool executed with test_value"}
    assert db_session.query(LogEntry).count() == 2


def test_handle_input_tool_fails(orchestrator, db_session):
    """Tests that if a tool raises an exception, it's handled gracefully."""
    # Re-patch the tool to raise an exception
    with patch.dict(
        orchestrator.available_tools,
        {"failing_tool": Mock(side_effect=Exception("Tool failed!"))},
    ):
        orchestrator.llm_service.choose_tool.return_value = {
            "name": "failing_tool",
            "arguments": {},
        }

        orchestrator.handle_player_input("Use the failing tool.", db_session)

        orchestrator.llm_service.choose_tool.assert_called_once()
        # Ensure the narrative is synthesized with the error message
        orchestrator.llm_service.synthesize_narrative.assert_called_once()
        # Check the arguments passed to the mock
        args, kwargs = orchestrator.llm_service.synthesize_narrative.call_args
        print(f"Called with args: {args}, kwargs: {kwargs}")
        assert args[1] == "failing_tool"
        assert "error" in kwargs["tool_result"]
        assert kwargs["tool_result"]["error"] == "Tool failed!"
        # The initial player log is committed, but the warden log for the failed action should not be
        assert db_session.query(LogEntry).count() == 1


def test_handle_input_unknown_tool(orchestrator, db_session):
    """Tests that a sensible response is generated if the LLM hallucinates a tool name."""
    orchestrator.llm_service.choose_tool.return_value = {
        "name": "nonexistent_tool",
        "arguments": {},
    }

    orchestrator.handle_player_input("Do something impossible.", db_session)

    orchestrator.llm_service.choose_tool.assert_called_once()
    orchestrator.llm_service.synthesize_narrative.assert_not_called()
    # Check that the final log entry contains the error message
    final_log = db_session.query(LogEntry).order_by(LogEntry.id.desc()).first()
    assert "Error: The AI tried to use an unknown tool" in final_log.content