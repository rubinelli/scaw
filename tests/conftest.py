"""
Configuration for the pytest test suite.
"""

import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path to allow for absolute imports
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, SRC_PATH)

from database.models import Base, GameEntity, MapPoint  # noqa: E402

# --- Database Fixtures ---


# Use an in-memory SQLite database for the entire test session
@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """Returns a SQLAlchemy session to the in-memory database."""
    connection = engine.connect()
    # Begin a non-ORM transaction
    transaction = connection.begin()
    # Bind an individual session to the connection
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    # Rollback the transaction to ensure a clean state for the next test
    transaction.rollback()
    connection.close()


# --- Game State Fixtures ---


@pytest.fixture
def test_character(db_session):
    """Creates a default player character for tests to use."""
    start_location = MapPoint(name="Testville", description="A town for testing.")
    character = GameEntity(
        name="Player",
        hp=10,
        max_hp=10,
        strength=11,
        max_strength=11,
        dexterity=12,
        max_dexterity=12,
        willpower=13,
        max_willpower=13,
        entity_type="Player",
        current_map_point=start_location,
    )
    db_session.add(character)
    db_session.commit()
    return character
