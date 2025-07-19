"""
Additional tests for the world_tools module to improve coverage.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, GameEntity, Item, Location, MapPoint
from core import world_tools

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


def test_drop_item(db_session):
    """Tests that a character can drop an item."""
    map_point = MapPoint(name="Test Point", status="explored")
    location = Location(name="Test Location", map_point=map_point)
    character = GameEntity(
        name="Test Character", entity_type="Character", current_location=location
    )
    item = Item(name="Sword", owner=character)
    db_session.add_all([map_point, location, character, item])
    db_session.commit()

    result = world_tools.drop_item(db_session, "Test Character", "Sword")

    assert result["success"] is True
    assert item.owner is None
    assert item.location is location


def test_increase_fatigue(db_session):
    """Tests that a character's fatigue can be increased."""
    character = GameEntity(
        name="Test Character", entity_type="Character", strength=5, fatigue=0
    )
    db_session.add(character)
    db_session.commit()

    result = world_tools.increase_fatigue(db_session, "Test Character")

    assert result["success"] is True
    assert character.fatigue == 1


def test_increase_fatigue_and_drop_item(db_session):
    """Tests that a character drops an item when fatigue exceeds strength."""
    map_point = MapPoint(name="Test Point", status="explored")
    location = Location(name="Test Location", map_point=map_point)
    character = GameEntity(
        name="Test Character",
        entity_type="Character",
        strength=1,
        fatigue=1,
        current_location=location,
    )
    item = Item(name="Heavy Armor", owner=character)
    db_session.add_all([map_point, location, character, item])
    db_session.commit()

    result = world_tools.increase_fatigue(db_session, "Test Character")

    assert result["success"] is True
    assert character.fatigue == 2
    assert item.owner is None
    assert item.location is location


def test_discover_location(db_session):
    """Tests that a hidden location can be discovered."""
    map_point = MapPoint(name="Hidden Place", status="hidden")
    db_session.add(map_point)
    db_session.commit()

    result = world_tools.discover_location(db_session, "Hidden Place")

    assert result["success"] is True
    assert map_point.status == "known"


def test_roll_wilderness_event(db_session):
    """Tests that a wilderness event can be rolled."""
    result = world_tools.roll_wilderness_event(db_session)
    assert "event_description" in result


def test_roll_saving_throw(db_session):
    """Tests that a saving throw can be rolled."""
    character = GameEntity(name="Test Character", entity_type="Character", strength=10)
    db_session.add(character)
    db_session.commit()

    result = world_tools.roll_saving_throw(db_session, "Test Character", "strength")

    assert "success" in result


def test_get_location_description(db_session):
    """Tests that a location description can be retrieved."""
    map_point = MapPoint(name="Test Point", status="explored")
    location = Location(
        name="Test Location", description="A test location.", map_point=map_point
    )
    character = GameEntity(
        name="Test Character", entity_type="Character", current_location=location
    )
    db_session.add_all([map_point, location, character])
    db_session.commit()

    result = world_tools.get_location_description(db_session, "Test Character")

    assert result["location_name"] == "Test Location"
    assert result["description"] == "A test location."


def test_move_character(db_session):
    """Tests that a character can be moved to a new location."""
    map_point = MapPoint(name="Test Point", status="explored")
    location1 = Location(name="Location 1", map_point=map_point)
    location2 = Location(name="Location 2", map_point=map_point)
    character = GameEntity(
        name="Test Character", entity_type="Character", current_location=location1
    )
    db_session.add_all([map_point, location1, location2, character])
    db_session.commit()

    result = world_tools.move_character(db_session, "Test Character", "Location 2")

    assert result["success"] is True
    assert character.current_location is location2
