"""
Test the tension event escalation system.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, TensionEvent, ResolutionCondition, GameEntity, LogEntry
from core.world_tools import make_camp, travel_to_map_point
from core.condition_tracker import ConditionTracker
import datetime


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_tension_event(db_session):
    """Create a sample tension event for testing."""
    event = TensionEvent(
        title="Test Crisis",
        description="A test crisis that needs resolution",
        source_type="test",
        source_data='{"test": true}',
        severity_level=1,
        max_severity=3,
        deadline_watches=2,
        watches_remaining=2,
        status="active"
    )
    db_session.add(event)
    db_session.commit()
    return event


@pytest.fixture
def sample_character(db_session):
    """Create a sample character for testing."""
    character = GameEntity(
        name="Test Character",
        entity_type="Character",
        hp=10,
        max_hp=10,
        strength=12,
        max_strength=12,
        dexterity=10,
        max_dexterity=10,
        willpower=8,
        max_willpower=8,
        fatigue=0,
        armor=0,
        is_retired=False
    )
    db_session.add(character)
    db_session.commit()
    return character


def test_condition_tracker_advance_time(db_session, sample_tension_event):
    """Test that advancing time reduces watches_remaining."""
    tracker = ConditionTracker(db_session)
    
    # Advance time by 1 watch
    escalated_events = tracker.advance_time(watches=1)
    
    # Refresh the event from database
    db_session.refresh(sample_tension_event)
    
    # Should have 1 watch remaining
    assert sample_tension_event.watches_remaining == 1
    assert len(escalated_events) == 0  # No escalation yet


def test_tension_event_escalation(db_session, sample_tension_event):
    """Test that tension events escalate when watches_remaining reaches 0."""
    tracker = ConditionTracker(db_session)
    
    # Advance time by 2 watches to trigger escalation
    escalated_events = tracker.advance_time(watches=2)
    
    # Refresh the event from database
    db_session.refresh(sample_tension_event)
    
    # Should have escalated to severity 2
    assert sample_tension_event.severity_level == 2
    assert sample_tension_event.watches_remaining == 2  # Reset to deadline_watches
    assert len(escalated_events) == 1
    assert escalated_events[0].id == sample_tension_event.id


def test_tension_event_failure(db_session):
    """Test that tension events fail when they reach max severity."""
    # Create an event at max severity
    event = TensionEvent(
        title="Failing Crisis",
        description="A crisis about to fail",
        source_type="test",
        source_data='{"test": true}',
        severity_level=3,
        max_severity=3,
        deadline_watches=1,
        watches_remaining=1,
        status="active"
    )
    db_session.add(event)
    db_session.commit()
    
    tracker = ConditionTracker(db_session)
    
    # Advance time to trigger failure
    escalated_events = tracker.advance_time(watches=1)
    
    # Refresh the event from database
    db_session.refresh(event)
    
    # Should have failed
    assert event.status == "failed"
    assert event.resolved_at is not None


@patch('core.llm_service.LLMService')
def test_make_camp_with_escalation(mock_llm_service, db_session, sample_character, sample_tension_event):
    """Test that make_camp advances time and handles escalations."""
    # Mock the LLM service to avoid API calls
    mock_llm_instance = Mock()
    mock_llm_service.return_value = mock_llm_instance
    mock_llm_instance.generate_tension_failure_consequences.return_value = "Test consequence"
    
    # Make camp should advance time by 1 watch
    result = make_camp(db_session, "Test Character")
    
    # Should succeed
    assert result["success"] is True
    assert "Time passes: 1 watch" in result["message"]
    assert result["time_advanced"] == 1
    
    # Check that the tension event was affected
    db_session.refresh(sample_tension_event)
    assert sample_tension_event.watches_remaining == 1


def test_multiple_escalations(db_session):
    """Test handling multiple tension events escalating simultaneously."""
    # Create multiple tension events
    events = []
    for i in range(3):
        event = TensionEvent(
            title=f"Crisis {i+1}",
            description=f"Test crisis {i+1}",
            source_type="test",
            source_data='{"test": true}',
            severity_level=1,
            max_severity=3,
            deadline_watches=1,
            watches_remaining=1,
            status="active"
        )
        db_session.add(event)
        events.append(event)
    
    db_session.commit()
    
    tracker = ConditionTracker(db_session)
    
    # Advance time to trigger all escalations
    escalated_events = tracker.advance_time(watches=1)
    
    # All events should have escalated
    assert len(escalated_events) == 3
    
    for event in events:
        db_session.refresh(event)
        assert event.severity_level == 2


def test_escalation_logging(db_session, sample_tension_event):
    """Test that escalations are properly logged."""
    tracker = ConditionTracker(db_session)
    
    # Count initial log entries
    initial_count = db_session.query(LogEntry).count()
    
    # Trigger escalation
    tracker.advance_time(watches=2)
    
    # Should have new log entries
    final_count = db_session.query(LogEntry).count()
    assert final_count > initial_count
    
    # Check that escalation was logged
    escalation_logs = db_session.query(LogEntry).filter(
        LogEntry.content.contains("ESCALATED")
    ).all()
    assert len(escalation_logs) > 0


if __name__ == "__main__":
    pytest.main([__file__])
