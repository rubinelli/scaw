import shlex
from typing import Callable, Dict, List, Tuple
from sqlalchemy.orm import Session

from core.llm_service import LLMService
from database.models import LogEntry, GameEntity, Item
import streamlit as st


class WardenOrchestrator:
    """Orchestrates the AI Warden's response to player input."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.command_handlers: Dict[
            str, Callable[..., str]
        ] = self._register_command_handlers()

    def _register_command_handlers(self) -> Dict[str, Callable[..., str]]:
        """Creates a dispatch table for slash commands."""
        return {
            "look": self._handle_look,
            "examine": self._handle_look,  # Alias for look
            "go": self._handle_go,
            "attack": self._handle_attack,
            # Future commands will be registered here
        }

    def _parse_command(self, player_input: str) -> Tuple[str, List[str]]:
        """Parses a slash command and its arguments.
        
        Handles quoted strings for multi-word arguments.
        Example: /attack "Cave Lizard" with sword
        Returns: ("attack", ["Cave Lizard", "with", "sword"])
        """
        if not player_input.startswith("/"):
            return "", [] # Not a slash command

        try:
            parts = shlex.split(player_input)
            if not parts: # Handle empty input after shlex.split
                return "", []
            command = parts[0][1:].lower()  # Remove slash and lowercase
            args = parts[1:]
            return command, args
        except ValueError:
            return "", []

    def handle_player_input(self, player_input: str, db: Session) -> None:
        """
        Processes player input, generates a response, and logs the interaction.
        """
        player_log = LogEntry(source="Player", content=player_input)
        db.add(player_log)
        db.commit()

        warden_response = ""
        if player_input.startswith("/"):
            command, args = self._parse_command(player_input)
            if command in self.command_handlers:
                handler = self.command_handlers[command]
                warden_response = handler(db, *args)
            else:
                warden_response = f"Unknown command: `/{command}`."
        else:
            warden_response = self.llm_service.generate_response(player_input)

        if warden_response:
            warden_log = LogEntry(source="Warden", content=warden_response)
            db.add(warden_log)
            db.commit()

    # --- Command Handlers ---

    def _handle_look(self, db: Session, *args: str) -> str:
        """Handles the /look command."""
        character_id = st.session_state.get('character_id')
        if not character_id:
            return "Error: Character not found in session."

        character = db.query(GameEntity).filter(GameEntity.id == character_id).first()
        if not character or not character.current_map_point:
            return "You are nowhere. This should not happen."

        current_map_point = character.current_map_point

        if not args:  # /look (no arguments)
            description_parts = [
                f"You are in {current_map_point.name}. {current_map_point.description or ''}"
            ]

            # Entities at this location (excluding the player character)
            entities_here = db.query(GameEntity).filter(
                GameEntity.current_map_point_id == current_map_point.id,
                GameEntity.id != character_id
            ).all()
            if entities_here:
                entity_names = [e.name for e in entities_here]
                description_parts.append(f"You see: {', '.join(entity_names)}.")

            # Items at this location (not in anyone's inventory)
            items_here = db.query(Item).filter(
                Item.location_id == current_map_point.id,
                Item.owner_entity_id == None # Items not owned by any entity
            ).all()
            if items_here:
                item_names = [i.name for i in items_here]
                description_parts.append(f"On the ground, you see: {', '.join(item_names)}.")

            prompt = " ".join(description_parts)
            return self.llm_service.generate_response(f"Describe the following scene in a vivid, concise way for a text-based adventure game: {prompt}")

        else:  # /look <target>
            target_name = " ".join(args).strip().lower()

            # Check for entities
            target_entity = db.query(GameEntity).filter(
                GameEntity.current_map_point_id == current_map_point.id,
                GameEntity.name.ilike(target_name)
            ).first()
            if target_entity:
                prompt = f"Describe {target_entity.name}, a {target_entity.entity_type}. Their description is: {target_entity.description or 'No specific description available.'} They have {target_entity.hp} HP, {target_entity.strength} STR, {target_entity.dexterity} DEX, {target_entity.willpower} WIL. Their disposition is {target_entity.disposition}."
                return self.llm_service.generate_response(f"Describe the following character in a vivid, concise way for a text-based adventure game: {prompt}")

            # Check for items
            target_item = db.query(Item).filter(
                Item.location_id == current_map_point.id,
                Item.owner_entity_id == None, # Only items on the ground
                Item.name.ilike(target_name)
            ).first()
            if target_item:
                prompt = f"Describe the item: {target_item.name}. Its description is: {target_item.description or 'No specific description available.'} It takes {target_item.slots} inventory slots."
                return self.llm_service.generate_response(f"Describe the following item in a vivid, concise way for a text-based adventure game: {prompt}")

            return f"You don't see '{target_name}' here."

    def _handle_go(self, db: Session, *args: str) -> str:
        """Handles the /go command. (Placeholder)"""
        destination = " ".join(args)
        if not destination:
            return "Where do you want to go? Usage: `/go <destination>`"
        return f"You attempt to go to {destination}. (Movement logic pending.)"

    def _handle_attack(self, db: Session, *args: str) -> str:
        """Handles the /attack command. (Placeholder)"""
        if not args:
            return "Who or what do you want to attack? Usage: `/attack <target>`"
        target = " ".join(args)
        return f"You attack the {target}! (Combat logic pending.)"