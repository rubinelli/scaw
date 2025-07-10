"""
Main orchestrator for the AI Warden.
"""

import inspect
from sqlalchemy.orm import Session
from core.llm_service import LLMService
from database.models import LogEntry
from core import world_tools


class WardenOrchestrator:
    """Orchestrates the AI Warden's response to player input."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.available_tools = self._load_tools()

    def _load_tools(self):
        """Dynamically loads all functions from the world_tools module."""
        return {
            name: func
            for name, func in inspect.getmembers(world_tools, inspect.isfunction)
            if not name.startswith("_")
        }

    def handle_player_input(self, player_input: str, db: Session) -> None:
        """
        Processes player input by using the LLM to select and execute a tool,
        then generates a narrative response.
        """
        player_log = LogEntry(source="Player", content=player_input)
        db.add(player_log)
        db.commit()

        chosen_tool_call = self.llm_service.choose_tool(
            player_input, tools=self.available_tools
        )

        warden_response = ""
        if chosen_tool_call:
            tool_name = chosen_tool_call.get("name")
            tool_args = chosen_tool_call.get("arguments", {})

            if tool_name in self.available_tools:
                tool_function = self.available_tools[tool_name]
                tool_args["db"] = db

                try:
                    tool_result = tool_function(**tool_args)
                    db.commit()  # Commit on success
                    warden_response = self.llm_service.synthesize_narrative(
                        player_input, tool_name, tool_result
                    )
                except Exception as e:
                    db.rollback()  # Rollback on failure
                    error_message = (
                        f"The attempt to use tool '{tool_name}' failed with error: {e}"
                    )
                    print(error_message)  # Log the full error for debugging
                    warden_response = self.llm_service.synthesize_narrative(
                        player_input, tool_name, tool_result={"error": str(e)}
                    )
            else:
                warden_response = (
                    f"Error: The AI tried to use an unknown tool: {tool_name}"
                )
        else:
            warden_response = self.llm_service.generate_response(player_input)

        if warden_response:
            warden_log = LogEntry(source="Warden", content=warden_response)
            db.add(warden_log)
            db.commit()
