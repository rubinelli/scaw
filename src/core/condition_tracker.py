"""
Condition Tracker Service

This module provides the ConditionTracker service that monitors game state changes
and automatically detects when resolution conditions for tension events are met.
"""

import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.models import TensionEvent, ResolutionCondition, GameEntity, LogEntry


class ConditionTracker:
    """Service to track and evaluate resolution conditions for tension events."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_all_conditions(self, trigger_type: str, trigger_data: Dict[str, Any]) -> None:
        """
        Check all active tension events for met conditions.
        
        Args:
            trigger_type: The type of trigger that occurred (e.g., "entity_death", "item_received")
            trigger_data: Data about the trigger event
        """
        active_events = self.db.query(TensionEvent).filter(TensionEvent.status == "active").all()
        
        for event in active_events:
            self._check_event_conditions(event, trigger_type, trigger_data)
    
    def _check_event_conditions(self, event: TensionEvent, trigger_type: str, trigger_data: Dict[str, Any]) -> None:
        """
        Check if any conditions for this specific event are now met.
        
        Args:
            event: The tension event to check
            trigger_type: The type of trigger that occurred
            trigger_data: Data about the trigger event
        """
        # Get unmet conditions for this event
        unmet_conditions = self.db.query(ResolutionCondition).filter(
            ResolutionCondition.tension_event_id == event.id,
            ResolutionCondition.is_met == False
        ).all()
        
        for condition in unmet_conditions:
            if self._evaluate_condition(condition, trigger_type, trigger_data):
                # Mark condition as met
                self.db.query(ResolutionCondition).filter(
                    ResolutionCondition.id == condition.id
                ).update({
                    "is_met": True,
                    "met_at": datetime.datetime.utcnow()
                })
                
                # Log the condition being met
                log_entry = LogEntry(
                    source="Warden",
                    content=f"**Condition Met:** {condition.description}",
                    metadata_dict={"tension_event_id": event.id, "condition_id": condition.id}
                )
                self.db.add(log_entry)
                
                # Check if all conditions for this event are now met
                remaining_unmet = self.db.query(ResolutionCondition).filter(
                    ResolutionCondition.tension_event_id == event.id,
                    ResolutionCondition.is_met == False
                ).count()
                
                if remaining_unmet == 0:
                    self._resolve_tension_event(event, str(condition.condition_type))
    
    def _evaluate_condition(self, condition: ResolutionCondition, trigger_type: str, trigger_data: Dict[str, Any]) -> bool:
        """
        Evaluate whether a specific condition is met by the current trigger.
        
        Args:
            condition: The condition to evaluate
            trigger_type: The type of trigger that occurred
            trigger_data: Data about the trigger event
            
        Returns:
            True if the condition is met, False otherwise
        """
        condition_type = str(condition.condition_type)
        
        if condition_type == "entity_death" and trigger_type == "entity_death":
            return self._check_entity_death_condition(condition, trigger_data)
        elif condition_type == "item_delivery" and trigger_type == "item_delivery":
            return self._check_item_delivery_condition(condition, trigger_data)
        elif condition_type == "item_received" and trigger_type == "item_received":
            return self._check_item_received_condition(condition, trigger_data)
        elif condition_type == "location_visit" and trigger_type == "location_visit":
            return self._check_location_visit_condition(condition, trigger_data)
        
        return False
    
    def _check_entity_death_condition(self, condition: ResolutionCondition, trigger_data: Dict[str, Any]) -> bool:
        """Check if an entity death condition is met."""
        target_data = condition.target_data
        
        # Flexible matching - can match by name or ID
        if "entity_name" in target_data:
            return trigger_data.get("entity_name", "").lower() == target_data["entity_name"].lower()
        elif "entity_id" in target_data:
            return trigger_data.get("entity_id") == target_data["entity_id"]
        
        return False
    
    def _check_item_delivery_condition(self, condition: ResolutionCondition, trigger_data: Dict[str, Any]) -> bool:
        """Check if an item delivery condition is met."""
        target_data = condition.target_data
        
        # Check if the right item was delivered to the right recipient
        item_name_match = "item_name" in target_data and trigger_data.get("item_name", "").lower() == target_data["item_name"].lower()
        receiver_name_match = "receiver_name" in target_data and trigger_data.get("receiver_name", "").lower() == target_data["receiver_name"].lower()
        
        return item_name_match and receiver_name_match
    
    def _check_item_received_condition(self, condition: ResolutionCondition, trigger_data: Dict[str, Any]) -> bool:
        """Check if an item received condition is met."""
        target_data = condition.target_data
        
        # Check if the right character received the right item
        item_name_match = "item_name" in target_data and trigger_data.get("item_name", "").lower() == target_data["item_name"].lower()
        recipient_name_match = "recipient_name" in target_data and trigger_data.get("recipient_name", "").lower() == target_data["recipient_name"].lower()
        
        return item_name_match and recipient_name_match
    
    def _check_location_visit_condition(self, condition: ResolutionCondition, trigger_data: Dict[str, Any]) -> bool:
        """Check if a location visit condition is met."""
        target_data = condition.target_data
        
        # Check if the right character visited the right location
        location_name_match = "location_name" in target_data and trigger_data.get("location_name", "").lower() == target_data["location_name"].lower()
        
        # If no specific character is required, any character visit counts
        if "character_name" not in target_data:
            return location_name_match
        
        character_name_match = trigger_data.get("character_name", "").lower() == target_data["character_name"].lower()
        return location_name_match and character_name_match
    
    def _resolve_tension_event(self, event: TensionEvent, resolution_method: str) -> None:
        """
        Mark a tension event as resolved and apply consequences.
        
        Args:
            event: The tension event to resolve
            resolution_method: How the event was resolved
        """
        # Update the event using SQLAlchemy's update method
        self.db.query(TensionEvent).filter(TensionEvent.id == event.id).update({
            "status": "resolved",
            "resolved_at": datetime.datetime.utcnow(),
            "resolution_method": resolution_method
        })
        
        # Log the resolution
        log_entry = LogEntry(
            source="Warden",
            content=f"**{event.title} - RESOLVED**\n\n{event.description}\n\nResolved through: {resolution_method}",
            metadata_dict={"tension_event_id": event.id, "resolution_method": resolution_method}
        )
        self.db.add(log_entry)
        
        # TODO: Apply resolution consequences (new tension events, world state changes, etc.)
        # This will be implemented in later tasks
        
        self.db.commit()
    
    def escalate_tension_events(self) -> List[TensionEvent]:
        """
        Check all active tension events and escalate those that have reached their deadline.
        This should be called periodically (e.g., when time advances).
        
        Returns:
            List of tension events that were escalated
        """
        # Query for events that need escalation
        events_to_escalate = self.db.query(TensionEvent).filter(
            TensionEvent.status == "active",
            TensionEvent.watches_remaining <= 0,
            TensionEvent.severity_level < TensionEvent.max_severity
        ).all()
        
        # Query for events that have failed (reached max severity)
        events_to_fail = self.db.query(TensionEvent).filter(
            TensionEvent.status == "active", 
            TensionEvent.watches_remaining <= 0,
            TensionEvent.severity_level >= TensionEvent.max_severity
        ).all()
        
        escalated_events = []
        
        # Handle escalations
        for event in events_to_escalate:
            new_severity = event.severity_level + 1
            self.db.query(TensionEvent).filter(TensionEvent.id == event.id).update({
                "severity_level": new_severity,
                "watches_remaining": event.deadline_watches
            })
            
            log_entry = LogEntry(
                source="Warden",
                content=f"**{event.title} - ESCALATED**\n\nSeverity increased to {new_severity}. The situation grows more dire!",
                metadata_dict={"tension_event_id": event.id, "new_severity": new_severity}
            )
            self.db.add(log_entry)
            escalated_events.append(event)
        
        # Handle failures
        for event in events_to_fail:
            self.db.query(TensionEvent).filter(TensionEvent.id == event.id).update({
                "status": "failed",
                "resolved_at": datetime.datetime.utcnow()
            })
            
            log_entry = LogEntry(
                source="Warden",
                content=f"**{event.title} - FAILED**\n\n{event.description}\n\nThe situation has spiraled out of control!",
                metadata_dict={"tension_event_id": event.id}
            )
            self.db.add(log_entry)
            
            # TODO: Apply failure consequences
            # This will be implemented in later tasks
        
        if escalated_events or events_to_fail:
            self.db.commit()
        
        return escalated_events
    
    def advance_time(self, watches: int = 1) -> List[TensionEvent]:
        """
        Advance time for all active tension events and check for escalations.
        
        Args:
            watches: Number of watches to advance
            
        Returns:
            List of tension events that were escalated or failed
        """
        # Update all active events' remaining watches
        self.db.query(TensionEvent).filter(TensionEvent.status == "active").update({
            "watches_remaining": TensionEvent.watches_remaining - watches
        }, synchronize_session=False)
        
        self.db.commit()
        
        return self.escalate_tension_events()
