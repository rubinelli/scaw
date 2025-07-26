import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, GameEntity
from core.world_tools import update_npc_relationship, get_npc_relationship_info


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_npc_relationship_system(db_session):
    """Test the NPC relationship management system."""
    # Create a test NPC
    npc = GameEntity(
        name="Test Merchant",
        entity_type="NPC",
        hp=10,
        max_hp=10,
        strength=12,
        max_strength=12,
        dexterity=10,
        max_dexterity=10,
        willpower=8,
        max_willpower=8,
        disposition="neutral"
    )
    db_session.add(npc)
    db_session.commit()
    
    # Test initial relationship
    info = get_npc_relationship_info(db_session, "Test Merchant")
    assert info["relationship_level"] == 0
    assert info["relationship_type"] == "neutral"
    assert info["trust_level"] == "cautious"
    assert info["fear_level"] == "none"
    
    # Test positive relationship change
    result = update_npc_relationship(
        db_session, "Test Merchant", "received_gift", 2, 
        "Grateful for the healing potion"
    )
    assert result["success"] == True
    assert result["new_level"] == 2
    assert result["disposition"] == "friendly"
    
    # Test negative relationship change
    result = update_npc_relationship(
        db_session, "Test Merchant", "witnessed_violence", -3,
        "Horrified by the brutal attack", fear_change="increase"
    )
    assert result["success"] == True
    assert result["new_level"] == -1
    assert result["disposition"] == "unfriendly"
    
    # Verify final state
    info = get_npc_relationship_info(db_session, "Test Merchant")
    assert info["relationship_level"] == -1
    assert info["relationship_type"] in ["suspicious", "resentful", "disappointed"]
    assert info["fear_level"] == "wary"
    assert len(info["recent_history"]) == 2


def test_relationship_bounds(db_session):
    """Test that relationship levels stay within bounds."""
    # Create a test NPC
    npc = GameEntity(
        name="Test Guard",
        entity_type="NPC",
        hp=15,
        max_hp=15,
        strength=14,
        max_strength=14,
        dexterity=12,
        max_dexterity=12,
        willpower=10,
        max_willpower=10,
        disposition="neutral"
    )
    db_session.add(npc)
    db_session.commit()
    
    # Test maximum positive relationship
    update_npc_relationship(db_session, "Test Guard", "heroic_deed", 10, "Saved the town")
    info = get_npc_relationship_info(db_session, "Test Guard")
    assert info["relationship_level"] == 5  # Should be capped at 5
    assert info["disposition"] == "allied"
    
    # Test maximum negative relationship
    update_npc_relationship(db_session, "Test Guard", "betrayal", -15, "Betrayed our trust")
    info = get_npc_relationship_info(db_session, "Test Guard")
    assert info["relationship_level"] == -5  # Should be capped at -5
    assert info["disposition"] == "hostile"
    assert npc.is_hostile == True
