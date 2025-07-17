"""
Tests for the world_tools module.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, GameEntity, Item
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


def test_roll_dice():
    result = world_tools.roll_dice("1d6")
    assert 1 <= result["total"] <= 6


def test_get_character_sheet(db_session):
    char = GameEntity(
        name="Test Character", entity_type="Character", hp=10, strength=12
    )
    db_session.add(char)
    db_session.commit()
    sheet = world_tools.get_character_sheet(db_session, "Test Character")
    assert sheet["name"] == "Test Character"
    assert sheet["hp"] == 10


def test_deal_damage(db_session):
    attacker = GameEntity(
        name="Attacker", entity_type="Character", attacks=[{"name": "Sword", "damage": "1d6"}]
    )
    target = GameEntity(
        name="Target", entity_type="Monster", hp=10, strength=12
    )
    db_session.add_all([attacker, target])
    db_session.commit()
    result = world_tools.deal_damage(db_session, "Attacker", "Target")
    assert result["new_hp"] < 10
    assert result["new_strength"] == 12


def test_deal_damage_with_scar(db_session):
    attacker = GameEntity(
        name="Attacker", entity_type="Character", attacks=[{"name": "Axe", "damage": "5"}]
    )
    target = GameEntity(
        name="Target", entity_type="Monster", hp=5, max_hp=5, strength=10
    )
    db_session.add_all([attacker, target])
    db_session.commit()

    # Damage brings HP to exactly 0, should trigger a scar
    result = world_tools.deal_damage(db_session, "Attacker", "Target")
    assert result["new_hp"] == 0
    assert result["new_strength"] == 10
    assert result["received_scar"] is not None
    assert target.max_hp == 4
    assert target.scars is not None

    # Further damage should go to strength
    attacker.attacks = [{"name": "Axe", "damage": "3"}]
    result = world_tools.deal_damage(db_session, "Attacker", "Target")
    assert result["new_hp"] == 0
    assert result["new_strength"] == 7
    assert result["received_scar"] is None


def test_add_item_to_inventory(db_session):
    char = GameEntity(name="Test Character", entity_type="Character")
    db_session.add(char)
    db_session.commit()
    world_tools.add_item_to_inventory(
        db_session, "Test Character", "Sword", description="A sharp sword."
    )
    db_session.commit()
    item = db_session.query(Item).filter_by(name="Sword").first()
    assert item is not None
    assert item.owner_entity_id == char.id


def test_rest(db_session):
    char = GameEntity(name="Test Character", entity_type="Character", hp=1, max_hp=10)
    db_session.add(char)
    db_session.commit()
    result = world_tools.rest(db_session, "Test Character")
    assert result["success"] is True
    assert char.hp == 10


def test_make_camp(db_session):
    char = GameEntity(name="Test Character", entity_type="Character", hp=1, max_hp=10)
    db_session.add(char)
    db_session.commit()
    result = world_tools.make_camp(db_session, "Test Character")
    assert result["success"] is True
    assert char.hp == 10

