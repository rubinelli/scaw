"""
Tests for the world_tools module.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, GameEntity, Item, MapPoint
from core import world_tools

# Use an in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def setup_test_data(db_session):
    """Fixture to populate the database with initial test data."""
    start_location = MapPoint(
        name="Start Town", description="A quiet town.", status="explored"
    )
    player = GameEntity(
        name="Player",
        hp=10,
        max_hp=10,
        strength=12,
        dexterity=14,
        willpower=10,
        fatigue=0,
        armor=1,
        is_retired=False,
        entity_type="Player",
        current_map_point=start_location,
    )
    goblin = GameEntity(
        name="Goblin",
        hp=6,
        max_hp=6,
        strength=8,
        dexterity=12,
        willpower=8,
        fatigue=0,
        armor=0,
        is_retired=False,
        entity_type="Monster",
        current_map_point=start_location,
    )
    sword = Item(name="Sword", description="A trusty blade.", owner=player)

    db_session.add_all([player, goblin, start_location, sword])
    db_session.commit()
    return player, goblin, start_location


# --- Test roll_dice ---
def test_roll_dice_simple():
    result = world_tools.roll_dice("1d6")
    assert 1 <= result["final_result"] <= 6
    assert len(result["rolls"]) == 1


def test_roll_dice_with_modifier():
    result = world_tools.roll_dice("2d8+2")
    assert 4 <= result["final_result"] <= 18
    assert len(result["rolls"]) == 2
    assert result["modifier"] == 2


# --- Test get_character_sheet ---
def test_get_character_sheet_found(db_session, setup_test_data):
    sheet = world_tools.get_character_sheet(db_session, "Player")
    assert sheet["name"] == "Player"
    assert sheet["hp"] == 10
    assert "Sword" in sheet["inventory"][0]


def test_get_character_sheet_not_found(db_session):
    sheet = world_tools.get_character_sheet(db_session, "Nonexistent")
    assert "error" in sheet


# --- Test deal_damage ---
def test_deal_damage_hp_only(db_session, setup_test_data):
    result = world_tools.deal_damage(db_session, "Goblin", 4)
    assert result["new_hp"] == 2
    assert result["new_strength"] == 8  # Strength should be unchanged
    assert not result["is_dead"]


def test_deal_damage_hp_and_strength(db_session, setup_test_data):
    result = world_tools.deal_damage(db_session, "Goblin", 8)
    assert result["new_hp"] == 0
    assert result["new_strength"] == 6  # 6 HP damage, 2 STR damage
    assert not result["is_dead"]


def test_deal_damage_lethal(db_session, setup_test_data):
    result = world_tools.deal_damage(db_session, "Goblin", 14)  # 6 HP + 8 STR
    assert result["is_dead"]
    # Verify the entity is marked as retired/deleted
    goblin = db_session.query(GameEntity).filter_by(name="Goblin").first()
    assert goblin is None


# --- Test add_item_to_inventory ---
def test_add_item_to_inventory_new(db_session, setup_test_data):
    result = world_tools.add_item_to_inventory(
        db_session, "Player", "Health Potion", 2, "A red potion."
    )
    assert result["success"]
    player = db_session.query(GameEntity).filter_by(name="Player").one()
    assert any(
        item.name == "Health Potion" and item.quantity == 2 for item in player.items
    )


def test_add_item_to_inventory_existing(db_session, setup_test_data):
    world_tools.add_item_to_inventory(db_session, "Player", "Rations", 1, "Food.")
    result = world_tools.add_item_to_inventory(db_session, "Player", "Rations", 2)
    assert result["success"]
    player = db_session.query(GameEntity).filter_by(name="Player").one()
    assert any(item.name == "Rations" and item.quantity == 3 for item in player.items)


# --- Test get_location_description ---
def test_get_location_description(db_session, setup_test_data):
    player, goblin, location = setup_test_data
    desc = world_tools.get_location_description(db_session, "Player")
    assert desc["location_name"] == "Start Town"
    assert "Goblin" in desc["other_entities_present"]
