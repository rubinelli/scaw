"""
Tests for the world_manager module.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, GameEntity, Location, MapPoint
from core.world_manager import WorldManager

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


def test_move_character_to_location(db_session):
    map_point = MapPoint(name="Test Map Point", description="A point on the map.", status="known")
    db_session.add(map_point)
    db_session.commit()

    char = GameEntity(name="Test Character", entity_type="Character")
    loc1 = Location(name="Location 1", map_point_id=map_point.id)
    loc2 = Location(name="Location 2", map_point_id=map_point.id)
    db_session.add_all([char, loc1, loc2])
    db_session.commit()
    char.current_location_id = loc1.id
    db_session.commit()

    manager = WorldManager(db_session)
    manager.move_character_to_location(char.id, loc2.id)

    assert char.current_location_id == loc2.id
