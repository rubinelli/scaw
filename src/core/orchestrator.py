import shlex
from typing import Any, Callable, Dict, List, Tuple
from sqlalchemy.orm import Session

from core.llm_service import LLMService
from database.models import LogEntry


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
        try:
            parts = shlex.split(player_input)
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
        """Handles the /look command. (Placeholder)"""
        target = " ".join(args) if args else "around"
        return f"You look {target}. (Full description pending.)"

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