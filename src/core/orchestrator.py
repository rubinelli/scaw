import inspect
from sqlalchemy.orm import Session
from core.llm_service import LLMService
from database.models import LogEntry, GameEntity, Item
from core import world_tools, world_manager


class WardenOrchestrator:
    """Orchestrates the AI Warden's response to player input."""

    def __init__(self, llm_service: LLMService, db: Session):
        self.llm_service = llm_service
        self.world_manager = world_manager.WorldManager(db)
        self.available_tools = self._load_tools()

    def _load_tools(self):
        """Dynamically loads all functions from the world_tools and world_manager modules."""
        tools = {}

        for name, func in inspect.getmembers(world_tools, inspect.isfunction):
            if not name.startswith("_"):
                tools[name] = func

        for name, func in inspect.getmembers(self.world_manager, inspect.ismethod):
            if not name.startswith("_"):
                tools[name] = func

        return tools

    def get_player_character(self, db: Session) -> GameEntity | None:
        """Retrieves the player character entity."""
        return db.query(GameEntity).filter_by(entity_type="Character", is_retired=False).first()

    def handle_player_input(self, player_input: str, db: Session) -> None:
        """
        Processes player input, executes a tool, handles NPC reactions,
        and generates a consolidated narrative response.
        """
        player_log = LogEntry(source="Player", content=player_input)
        db.add(player_log)
        db.commit()  # Commit the player log immediately

        # --- Context Gathering Step ---
        player = self.get_player_character(db)
        context_prompt = ""
        if player and player.current_location:
            location_name = player.current_location.name
            entities_at_location = (
                db.query(GameEntity)
                .filter(
                    GameEntity.current_location_id == player.current_location_id,
                    #GameEntity.is_retired == False,  # noqa: E712
                    GameEntity.id != player.id,  # Exclude the player character
                )
                .all()
            )
            items_at_location = (
                db.query(Item)
                .filter(Item.location_id == player.current_location_id)
                .all()
            )

            entity_names = [e.name + ("(dead)" if e.is_retired else "") for e in entities_at_location]
            item_names = [i.name for i in items_at_location]
            context_list = entity_names + item_names
            context_names = ", ".join(context_list) or "nothing of interest" # type: ignore

            context_prompt = f"""
You are at: {location_name}.
The following are here: {context_names}.
"""

        # --- Tool Selection Step ---
        prompt_for_llm = f"{context_prompt}\nPlayer command: {player_input}"
        print(f"Prompt for LLM: {prompt_for_llm}")
        chosen_tool_call = self.llm_service.choose_tool(
            prompt_for_llm, tools=self.available_tools
        )

        player_action_result = None
        tool_name = "N/A"
        warden_response = ""

        if chosen_tool_call:
            print(f"Chosen tool call: {chosen_tool_call}")
            tool_name = str(chosen_tool_call.get("name"))
            tool_args = chosen_tool_call.get("arguments", {})

            if tool_name in self.available_tools:
                tool_function = self.available_tools[tool_name]
                try:
                    # Inject the db session into the arguments if required
                    if "db" in inspect.signature(tool_function).parameters:
                        tool_args["db"] = db

                    player_action_result = tool_function(**tool_args)
                    db.commit()  # Commit after successful tool use
                except Exception as e:
                    db.rollback()
                    player_action_result = {
                        "error": f"The attempt to use tool '{tool_name}' failed: {e}"
                    }
            else:
                player_action_result = {
                    "error": f"The AI tried to use an unknown tool: {tool_name}"
                }
        else:
            print("No tool was called by the AI.")

        # --- NPC Reaction Step ---
        npc_actions = []
        player = self.get_player_character(db)
        if player and player.current_location:
            hostile_npcs = (
                db.query(GameEntity)
                .filter(
                    GameEntity.current_location_id == player.current_location_id,
                    GameEntity.is_hostile == True,  # noqa: E712
                    GameEntity.is_retired == False,  # noqa: E712
                    GameEntity.id != player.id,
                )
                .all()
            )

            for npc in hostile_npcs:
                # Simple NPC AI: always attack the player
                attack_result = world_tools.deal_damage(
                    db, attacker_name=npc.name, target_name=player.name
                )
                npc_actions.append({npc.name: attack_result})
                db.commit() # Commit each NPC action

        # --- Narrative Synthesis Step ---
        if player_action_result or npc_actions:
            narrative_prompt = f"""
            The player's action was: "{player_input}"
            The result of their action was: {player_action_result}
            After the player's action, the following NPCs reacted: {npc_actions}

            Synthesize these events into a single, compelling narrative for the player.
            """
            warden_response = self.llm_service.generate_response(narrative_prompt)
        else:
            # If no tool was called and no NPCs reacted, get a standard response
            warden_response = self.llm_service.generate_response(player_input)

        if warden_response:
            warden_log = LogEntry(source="Warden", content=warden_response)
            db.add(warden_log)

        db.commit()
