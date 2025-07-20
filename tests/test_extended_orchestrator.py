"""
Additional tests for the orchestrator module to improve coverage.
"""

import pytest
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, GameEntity, Location, MapPoint, LogEntry
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


def test_handle_input_tool_fails(orchestrator, db_session):
    """Tests that an error is handled gracefully if a tool fails."""
    orchestrator.llm_service.choose_tool.return_value = {
        "name": "deal_damage",
        "arguments": {"attacker_name": "Player", "target_name": "Nonexistent"},
    }

    orchestrator.handle_player_input("I attack the nonexistent target!", db_session)

    orchestrator.llm_service.choose_tool.assert_called_once()
    orchestrator.llm_service.generate_response.assert_called_once()
    # Check that a narrative was still generated, likely an error message
    assert db_session.query(LogEntry).count() == 2


def test_npc_reaction_non_attack(orchestrator, db_session):
    """Tests that a hostile NPC does not react if the player's action is not an attack."""
    # Setup the world
    map_point = MapPoint(
        name="Dark Cave", status="known", summary="A dark and spooky cave."
    )
    location = Location(
        name="Cave Interior", description="A dark cave.", map_point=map_point
    )
    player = GameEntity(
        name="Player",
        entity_type="Character",
        hp=10,
        strength=10,
        current_location=location,
        current_map_point=map_point,
    )
    goblin = GameEntity(
        name="Goblin",
        entity_type="Monster",
        hp=5,
        strength=5,
        is_hostile=True,
        current_location=location,
        current_map_point=map_point,
        attacks='[{"name": "Club", "damage": "1d4"}]',
    )
    db_session.add_all([map_point, location, player, goblin])
    db_session.commit()

    orchestrator.llm_service.choose_tool.return_value = {
        "name": "roll_dice",
        "arguments": {"dice_string": "1d6"},
    }

    orchestrator.handle_player_input("I roll a die.", db_session)

    # Verify player's HP is unchanged
    assert player.hp == 10

    # Verify narrative was generated
    orchestrator.llm_service.generate_response.assert_called_once()
    assert db_session.query(LogEntry).filter_by(source="Warden").count() == 1
