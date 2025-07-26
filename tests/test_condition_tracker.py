"""
Tests for the ConditionTracker service.
"""

import pytest
import datetime
from unittest.mock import Mock
from sqlalchemy.orm import Session
from core.condition_tracker import ConditionTracker
from database.models import TensionEvent, ResolutionCondition, LogEntry


class TestConditionTracker:
    """Test cases for the ConditionTracker service."""
    
    def test_init(self):
        """Test ConditionTracker initialization."""
        mock_db = Mock(spec=Session)
        tracker = ConditionTracker(mock_db)
        assert tracker.db == mock_db
    
    def test_check_entity_death_condition_by_name(self):
        """Test entity death condition matching by name."""
        mock_db = Mock(spec=Session)
        tracker = ConditionTracker(mock_db)
        
        # Create a mock condition
        condition = Mock()
        condition.target_data = {"entity_name": "Goblin"}
        
        # Test matching trigger data
        trigger_data = {"entity_name": "Goblin"}
        assert tracker._check_entity_death_condition(condition, trigger_data) == True
        
        # Test non-matching trigger data
        trigger_data = {"entity_name": "Orc"}
        assert tracker._check_entity_death_condition(condition, trigger_data) == False
        
        # Test case insensitive matching
        trigger_data = {"entity_name": "goblin"}
        assert tracker._check_entity_death_condition(condition, trigger_data) == True
    
    def test_check_entity_death_condition_by_id(self):
        """Test entity death condition matching by ID."""
        mock_db = Mock(spec=Session)
        tracker = ConditionTracker(mock_db)
        
        # Create a mock condition
        condition = Mock()
        condition.target_data = {"entity_id": 123}
        
        # Test matching trigger data
        trigger_data = {"entity_id": 123}
        assert tracker._check_entity_death_condition(condition, trigger_data) == True
        
        # Test non-matching trigger data
        trigger_data = {"entity_id": 456}
        assert tracker._check_entity_death_condition(condition, trigger_data) == False
    
    def test_check_item_delivery_condition(self):
        """Test item delivery condition matching."""
        mock_db = Mock(spec=Session)
        tracker = ConditionTracker(mock_db)
        
        # Create a mock condition
        condition = Mock()
        condition.target_data = {
            "item_name": "Healing Potion",
            "receiver_name": "Village Elder"
        }
        
        # Test matching trigger data
        trigger_data = {
            "item_name": "Healing Potion",
            "receiver_name": "Village Elder"
        }
        assert tracker._check_item_delivery_condition(condition, trigger_data) == True
        
        # Test non-matching item
        trigger_data = {
            "item_name": "Sword",
            "receiver_name": "Village Elder"
        }
        assert tracker._check_item_delivery_condition(condition, trigger_data) == False
        
        # Test non-matching receiver
        trigger_data = {
            "item_name": "Healing Potion",
            "receiver_name": "Blacksmith"
        }
        assert tracker._check_item_delivery_condition(condition, trigger_data) == False
        
        # Test case insensitive matching
        trigger_data = {
            "item_name": "healing potion",
            "receiver_name": "village elder"
        }
        assert tracker._check_item_delivery_condition(condition, trigger_data) == True
    
    def test_check_location_visit_condition(self):
        """Test location visit condition matching."""
        mock_db = Mock(spec=Session)
        tracker = ConditionTracker(mock_db)
        
        # Create a mock condition with specific character requirement
        condition = Mock()
        condition.target_data = {
            "location_name": "Old Mill",
            "character_name": "Player"
        }
        
        # Test matching trigger data
        trigger_data = {
            "location_name": "Old Mill",
            "character_name": "Player"
        }
        assert tracker._check_location_visit_condition(condition, trigger_data) == True
        
        # Test non-matching location
        trigger_data = {
            "location_name": "Tavern",
            "character_name": "Player"
        }
        assert tracker._check_location_visit_condition(condition, trigger_data) == False
        
        # Test condition without character requirement (any character can visit)
        condition.target_data = {"location_name": "Old Mill"}
        trigger_data = {
            "location_name": "Old Mill",
            "character_name": "Anyone"
        }
        assert tracker._check_location_visit_condition(condition, trigger_data) == True
    
    def test_evaluate_condition_type_matching(self):
        """Test that condition evaluation matches correct types."""
        mock_db = Mock(spec=Session)
        tracker = ConditionTracker(mock_db)
        
        # Mock condition
        condition = Mock()
        condition.condition_type = "entity_death"
        condition.target_data = {"entity_name": "Goblin"}
        
        # Test matching condition type
        assert tracker._evaluate_condition(condition, "entity_death", {"entity_name": "Goblin"}) == True
        
        # Test non-matching condition type
        assert tracker._evaluate_condition(condition, "item_delivery", {"entity_name": "Goblin"}) == False
    
    def test_resolve_tension_event(self):
        """Test tension event resolution."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        
        tracker = ConditionTracker(mock_db)
        
        # Create mock event
        event = Mock()
        event.id = 1
        event.title = "Test Event"
        event.description = "Test Description"
        
        # Call resolve method
        tracker._resolve_tension_event(event, "entity_death")
        
        # Verify database update was called
        mock_db.query.assert_called()
        mock_filter.update.assert_called_once()
        
        # Verify log entry was added
        mock_db.add.assert_called()
        mock_db.commit.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
