import pytest
from unittest.mock import Mock, patch
from core.orchestrator import WardenOrchestrator
from database.models import LogEntry, GameEntity, MapPoint, Item


@pytest.fixture
def mock_llm_service():
    """Fixture for a mocked LLMService."""
    mock = Mock()
    mock.generate_response.return_value = "LLM response."
    return mock


@pytest.fixture
def mock_db_session():
    """Fixture for a mocked SQLAlchemy Session."""
    mock = Mock()
    # Mock the query method to return an object that can be chained
    mock_query_result = Mock()
    mock.query.return_value = mock_query_result

    # Mock the filter method to return an object that can be chained
    mock_filter_result = Mock()
    mock_query_result.filter.return_value = mock_filter_result

    # Default return values for first() and all()
    mock_filter_result.first.return_value = None
    mock_filter_result.all.return_value = []

    return mock


@pytest.fixture
def orchestrator(mock_llm_service):
    """Fixture for a WardenOrchestrator instance."""
    return WardenOrchestrator(mock_llm_service)


# --- Test _parse_command ---
def test_parse_command_basic(orchestrator):
    command, args = orchestrator._parse_command("/look")
    assert command == "look"
    assert args == []


def test_parse_command_single_arg(orchestrator):
    command, args = orchestrator._parse_command("/go north")
    assert command == "go"
    assert args == ["north"]


def test_parse_command_multiple_args(orchestrator):
    command, args = orchestrator._parse_command("/attack goblin with sword")
    assert command == "attack"
    assert args == ["goblin", "with", "sword"]


def test_parse_command_quoted_arg(orchestrator):
    command, args = orchestrator._parse_command('/look "old chest"')
    assert command == "look"
    assert args == ["old chest"]


def test_parse_command_mixed_args(orchestrator):
    command, args = orchestrator._parse_command('/use potion "on self"')
    assert command == "use"
    assert args == ["potion", "on self"]


def test_parse_command_empty_input(orchestrator):
    command, args = orchestrator._parse_command("")
    assert command == ""
    assert args == []


def test_parse_command_no_slash(orchestrator):
    command, args = orchestrator._parse_command("look around")
    assert command == ""
    assert args == []


# --- Test handle_player_input ---
@patch("core.orchestrator.st")  # Mock streamlit
def test_handle_player_input_recognized_command(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    mock_character = Mock(spec=GameEntity, id=1)
    mock_map_point = Mock(
        spec=MapPoint, id=1, name="Forest", description="A dark forest."
    )
    mock_character.current_map_point = mock_map_point
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_character
    )

    orchestrator.handle_player_input("/look", mock_db_session)

    mock_db_session.add.assert_called()  # For player log
    mock_db_session.commit.assert_called()  # For player log
    mock_db_session.add.assert_called()  # For warden log
    mock_db_session.commit.assert_called()  # For warden log
    orchestrator.llm_service.generate_response.assert_called_once()  # LLM is called by _handle_look


@patch("core.orchestrator.st")  # Mock streamlit
def test_handle_player_input_unknown_command(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    orchestrator.handle_player_input("/unknowncommand", mock_db_session)

    mock_db_session.add.assert_called()  # For player log
    mock_db_session.commit.assert_called()  # For player log
    # Expecting a warden response about unknown command, so warden log should be added
    assert any(
        isinstance(call.args[0], LogEntry) and "Unknown command" in call.args[0].content
        for call in mock_db_session.add.call_args_list
    )
    mock_db_session.commit.assert_called()  # For warden log
    orchestrator.llm_service.generate_response.assert_not_called()


@patch("core.orchestrator.st")  # Mock streamlit
def test_handle_player_input_natural_language(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    orchestrator.handle_player_input("I want to open the door.", mock_db_session)

    mock_db_session.add.assert_called()  # For player log
    mock_db_session.commit.assert_called()  # For player log
    orchestrator.llm_service.generate_response.assert_called_once_with(
        "I want to open the door."
    )
    mock_db_session.add.assert_called()  # For warden log
    mock_db_session.commit.assert_called()  # For warden log


# --- Test _handle_look ---
@patch("core.orchestrator.st")
def test_handle_look_no_args_no_entities_or_items(
    mock_st, orchestrator, mock_db_session
):
    mock_st.session_state = {"character_id": 1}
    mock_character = Mock(spec=GameEntity, id=1)
    mock_map_point = Mock(spec=MapPoint)
    mock_map_point.id = 1
    mock_map_point.name = "Clearing"
    mock_map_point.description = "A small clearing in the woods."
    mock_character.current_map_point = mock_map_point

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_character
    )
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [
        [],
        [],
    ]  # No entities, no items

    response = orchestrator._handle_look(mock_db_session)
    assert "LLM response." in response
    orchestrator.llm_service.generate_response.assert_called_once()
    expected_prompt_part = "You are in Clearing. A small clearing in the woods."
    assert (
        expected_prompt_part
        in orchestrator.llm_service.generate_response.call_args[0][0]
    )


@patch("core.orchestrator.st")
def test_handle_look_no_args_with_entities(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    mock_character = Mock(spec=GameEntity, id=1)
    mock_map_point = Mock(spec=MapPoint)
    mock_map_point.id = 1
    mock_map_point.name = "Clearing"
    mock_map_point.description = "A small clearing in the woods."
    mock_character.current_map_point = mock_map_point

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_character
    )

    mock_goblin = Mock(spec=GameEntity)
    mock_goblin.name = "Goblin"
    mock_goblin.entity_type = "NPC"
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [
        [mock_goblin],  # For entities_here
        [],  # For items_here
    ]

    response = orchestrator._handle_look(mock_db_session)
    assert "LLM response." in response
    orchestrator.llm_service.generate_response.assert_called_once()
    assert (
        "You see: Goblin." in orchestrator.llm_service.generate_response.call_args[0][0]
    )


@patch("core.orchestrator.st")
def test_handle_look_no_args_with_items(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    mock_character = Mock(spec=GameEntity, id=1)
    mock_map_point = Mock(spec=MapPoint)
    mock_map_point.id = 1
    mock_map_point.name = "Clearing"
    mock_map_point.description = "A small clearing in the woods."
    mock_character.current_map_point = mock_map_point

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_character
    )

    mock_sword = Mock(spec=Item)
    mock_sword.name = "Sword"
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [
        [],  # For entities_here
        [mock_sword],  # For items_here
    ]

    response = orchestrator._handle_look(mock_db_session)
    assert "LLM response." in response
    orchestrator.llm_service.generate_response.assert_called_once()
    assert (
        "On the ground, you see: Sword."
        in orchestrator.llm_service.generate_response.call_args[0][0]
    )


@patch("core.orchestrator.st")
def test_handle_look_target_entity_found(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    mock_character = Mock(spec=GameEntity, id=1)
    mock_map_point = Mock(spec=MapPoint)
    mock_map_point.id = 1
    mock_map_point.name = "Clearing"
    mock_character.current_map_point = mock_map_point

    mock_goblin = Mock(spec=GameEntity)
    mock_goblin.name = "Goblin"
    mock_goblin.entity_type = "Monster"
    mock_goblin.description = "A small, green-skinned creature."
    mock_goblin.hp = 5
    mock_goblin.strength = 10
    mock_goblin.dexterity = 8
    mock_goblin.willpower = 6
    mock_goblin.disposition = "hostile"

    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_character,  # For character query
        mock_goblin,  # For target entity query
    ]

    response = orchestrator._handle_look(mock_db_session, "goblin")
    assert "LLM response." in response
    orchestrator.llm_service.generate_response.assert_called_once()
    assert (
        "Describe Goblin, a Monster."
        in orchestrator.llm_service.generate_response.call_args[0][0]
    )


@patch("core.orchestrator.st")
def test_handle_look_target_item_found(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    mock_character = Mock(spec=GameEntity, id=1)
    mock_map_point = Mock(spec=MapPoint)
    mock_map_point.id = 1
    mock_map_point.name = "Clearing"
    mock_character.current_map_point = mock_map_point

    mock_sword = Mock(spec=Item)
    mock_sword.name = "Rusty Sword"
    mock_sword.description = "A rusty, old sword."
    mock_sword.slots = 2

    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_character,  # For character query
        None,  # No entity found
        mock_sword,  # For target item query
    ]

    response = orchestrator._handle_look(mock_db_session, "rusty sword")
    assert "LLM response." in response
    orchestrator.llm_service.generate_response.assert_called_once()
    assert (
        "Describe the item: Rusty Sword."
        in orchestrator.llm_service.generate_response.call_args[0][0]
    )


@patch("core.orchestrator.st")
def test_handle_look_target_not_found(mock_st, orchestrator, mock_db_session):
    mock_st.session_state = {"character_id": 1}
    mock_character = Mock(spec=GameEntity, id=1)
    mock_map_point = Mock(spec=MapPoint)
    mock_map_point.id = 1
    mock_map_point.name = "Clearing"
    mock_character.current_map_point = mock_map_point

    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_character,  # For character query
        None,  # No entity found
        None,  # No item found
    ]

    response = orchestrator._handle_look(mock_db_session, "nonexistent thing")
    assert "You don't see 'nonexistent thing' here." == response
    orchestrator.llm_service.generate_response.assert_not_called()
