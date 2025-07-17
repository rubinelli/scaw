"""
Manages the state of the world, including map points and their connections.
"""

from sqlalchemy.orm import Session
from database import models


class WorldManager:
    """Handles the logic for the game world's structure and state."""

    def __init__(self, db: Session):
        self.db = db

    def move_character_to_location(
        self, character_id: int, new_location_id: int
    ) -> dict:
        """
        Moves a character to a new location, updating their current position.

        Args:
            character_id: The ID of the character to move.
            new_location_id: The ID of the location to move to.

        Returns:
            A dictionary indicating the result of the move.
        """
        character = (
            self.db.query(models.GameEntity)
            .filter_by(id=character_id)
            .first()
        )
        new_location = (
            self.db.query(models.Location)
            .filter_by(id=new_location_id)
            .first()
        )

        if not character:
            return {"error": f"Character with ID {character_id} not found."}
        if not new_location:
            return {"error": f"Location with ID {new_location_id} not found."}

        # Check for a valid connection if we want to enforce it
        # For now, we'll allow free movement to any known location.

        character.current_location_id = new_location.id

        return {
            "success": True,
            "character_name": character.name,
            "new_location_name": new_location.name,
        }
