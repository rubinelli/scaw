from sqlalchemy.orm import Session
from core.llm_service import LLMService
from database.models import LogEntry


class WardenOrchestrator:
    """Orchestrates the AI Warden's response to player input."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def handle_player_input(self, player_input: str, db: Session):
        """Processes player input, generates a response, and logs the interaction."""
        # 1. Log the player's action
        player_log = LogEntry(source="Player", content=player_input)
        db.add(player_log)
        db.commit()

        warden_response = ""
        # 2. Parse the input and generate a response
        if player_input.startswith("/"):
            # Simple placeholder for slash commands for now
            warden_response = self._handle_slash_command(player_input)
        else:
            # Pass natural language to the LLM
            warden_response = self.llm_service.generate_response(player_input)

        # 3. Log the Warden's response
        if warden_response:
            warden_log = LogEntry(source="Warden", content=warden_response)
            db.add(warden_log)
            db.commit()

    def _handle_slash_command(self, command: str) -> str:
        """Private method to handle slash command parsing."""
        # In the future, this will have complex logic.
        # For now, it just acknowledges the command.
        return f"Acknowledge command: `{command}`. (Full implementation pending.)"
