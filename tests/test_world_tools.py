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
    char = GameEntity(name="Test Character", entity_type="Character", hp=10, strength=12)
    db_session.add(char)
    db_session.commit()
    sheet = world_tools.get_character_sheet(db_session, "Test Character")
    assert sheet["name"] == "Test Character"
    assert sheet["hp"] == 10


def test_deal_damage(db_session):
    char = GameEntity(name="Test Character", entity_type="Character", hp=10, strength=12)
    db_session.add(char)
    db_session.commit()
    result = world_tools.deal_damage(db_session, "Test Character", 5)
    assert result["new_hp"] == 5
    assert result["new_strength"] == 12
    result = world_tools.deal_damage(db_session, "Test Character", 15)
    assert result["new_hp"] == 0
    assert result["new_strength"] == 2
    assert result["is_dead"] == False


def test_add_item_to_inventory(db_session):
    char = GameEntity(name="Test Character", entity_type="Character")
    db_session.add(char)
    db_session.commit()
    world_tools.add_item_to_inventory(db_session, "Test Character", "Sword", description="A sharp sword.")
    db_session.commit()
    item = db_session.query(Item).filter_by(name="Sword").first()
    assert item is not None
    assert item.owner_entity_id == char.id