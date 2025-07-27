import inspect
import random
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
        return (
            db.query(GameEntity)
            .filter_by(entity_type="Character", is_retired=False)
            .first()
        )

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
            location_description = player.current_location.description
            map_point_summary = player.current_map_point.summary
            entities_at_location = (
                db.query(GameEntity)
                .filter(
                    GameEntity.current_location_id == player.current_location_id,
                    GameEntity.id != player.id,  # Exclude the player character
                )
                .all()
            )
            items_at_location = (
                db.query(Item)
                .filter(Item.location_id == player.current_location_id)
                .all()
            )

            entity_names = [
                e.name + ("(dead)" if e.is_retired else "")
                for e in entities_at_location
            ]
            item_names = [i.name for i in items_at_location]
            context_list = entity_names + item_names
            context_names = ", ".join(context_list) or "nothing of interest"  # type: ignore

            context_prompt = f"""
**CURRENT SCENE:**
Area Overview: {map_point_summary}
Immediate Location: {location_name} - {location_description}
Present: {context_names}

**ATMOSPHERE CUES:**
- Consider the time of day and weather
- Factor in recent events and their emotional aftermath  
- Note the tension level based on who/what is present
- Include environmental sounds and smells appropriate to the location

**NARRATIVE FOCUS:**
- Describe the player's immediate surroundings with rich sensory detail
- Show how NPCs react to the player's presence and recent actions
- Hint at potential dangers or opportunities in the environment
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

        # --- Proactive NPC Actions Step ---
        proactive_action = self._check_proactive_npc_actions(db)
        if proactive_action:
            npc_actions = [proactive_action]
        else:
            npc_actions = []

        # --- NPC Reaction Step ---
        # Enhanced NPC reactions based on player actions
        if player_action_result and not player_action_result.get("error"):
            npc_reactions = self._generate_npc_reactions(db, player_input, tool_name, player_action_result)
            npc_actions.extend(npc_reactions)

        # Combat reactions (hostile NPCs attack after player deals damage)
        if tool_name == "deal_damage":
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
                    npc_actions.append({f"{npc.name}_combat": attack_result})
                    db.commit()  # Commit each NPC action

        # --- Narrative Synthesis Step ---
        if player_action_result or npc_actions:
            # Use synthesize_narrative for tool-based actions with conversation context
            if player_action_result and not player_action_result.get("error"):
                warden_response = self.llm_service.synthesize_narrative(
                    player_input, tool_name, player_action_result, db
                )
                
                # If there were NPC reactions, append them to the narrative
                if npc_actions:
                    npc_narrative_prompt = f"""
                    After the main action, the following NPCs reacted: {npc_actions}
                    
                    Add a brief continuation to describe these NPC reactions, maintaining the same 
                    immersive style. Keep it to 1-2 sentences maximum.
                    """
                    npc_narrative = self.llm_service.generate_response(npc_narrative_prompt)
                    warden_response += f" {npc_narrative}"
            else:
                # For errors or pure NPC actions, use the original approach
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

    def _check_proactive_npc_actions(self, db: Session):
        """Occasionally have NPCs act independently"""
        if random.random() < 0.05:  # 5% chance per turn
            player = self.get_player_character(db)
            if player and player.current_location:
                npcs = (
                    db.query(GameEntity)
                    .filter(
                        GameEntity.current_location_id == player.current_location_id,
                        GameEntity.entity_type == "NPC",
                        GameEntity.is_retired == False,  # noqa: E712
                        GameEntity.id != player.id,
                    )
                    .all()
                )
                
                if npcs:
                    chosen_npc = random.choice(npcs)
                    return self._generate_npc_proactive_action(chosen_npc, db)
        
        return None

    def _generate_npc_proactive_action(self, npc: GameEntity, db: Session):
        """Generate a proactive action for an NPC"""
        # Get NPC relationship info for context
        relationship_info = world_tools.get_npc_relationship_info(db, npc.name)
        
        context = f"""
        NPC: {npc.name} - {npc.description}
        Disposition: {npc.disposition}
        Relationship: {relationship_info.get('relationship_type', 'neutral')}
        Trust Level: {relationship_info.get('trust_level', 'cautious')}
        Fear Level: {relationship_info.get('fear_level', 'none')}
        """
        
        action_description = self.llm_service.generate_npc_reaction(
            npc.name, npc.description, "acting independently", context
        )
        
        return {f"{npc.name}_proactive": {"description": action_description}}

    def _generate_npc_reactions(self, db: Session, player_input: str, tool_name: str, tool_result: dict):
        """Generate NPC reactions to player actions"""
        reactions = []
        player = self.get_player_character(db)
        
        if not player or not player.current_location:
            return reactions
        
        # Get all NPCs at the current location
        npcs = (
            db.query(GameEntity)
            .filter(
                GameEntity.current_location_id == player.current_location_id,
                GameEntity.entity_type == "NPC",
                GameEntity.is_retired == False,  # noqa: E712
                GameEntity.id != player.id,
            )
            .all()
        )
        
        for npc in npcs:
            # Skip if this NPC is hostile and will attack anyway
            if npc.is_hostile and tool_name == "deal_damage":
                continue
                
            # Update relationships based on player actions
            self._update_npc_relationship_for_action(db, npc, tool_name, tool_result)
            
            # Generate reaction based on the action
            if self._should_npc_react(npc, tool_name):
                relationship_info = world_tools.get_npc_relationship_info(db, npc.name)
                
                context = f"""
                Player Action: {player_input}
                Tool Used: {tool_name}
                Result: {tool_result}
                NPC Disposition: {npc.disposition}
                Relationship: {relationship_info.get('relationship_type', 'neutral')}
                """
                
                reaction = self.llm_service.generate_npc_reaction(
                    npc.name, npc.description, player_input, context
                )
                
                reactions.append({f"{npc.name}_reaction": {"description": reaction}})
        
        return reactions

    def _update_npc_relationship_for_action(self, db: Session, npc: GameEntity, tool_name: str, tool_result: dict):
        """Update NPC relationships based on player actions"""
        if tool_name == "deal_damage" and not tool_result.get("error"):
            # Witnessing violence makes NPCs fearful/hostile
            target_name = tool_result.get("target_name", "")
            if target_name != npc.name:  # NPC witnessed violence against someone else
                world_tools.update_npc_relationship(
                    db, npc.name, "witnessed_violence", -1,
                    f"Disturbed by the violence against {target_name}",
                    fear_change="increase"
                )
        elif tool_name == "give_item":
            # Already handled in the give_item function
            pass
        elif tool_name == "rest":
            # Peaceful actions might slightly improve relationships
            world_tools.update_npc_relationship(
                db, npc.name, "peaceful_action", 0,
                "Noticed the peaceful behavior"
            )

    def _should_npc_react(self, npc: GameEntity, tool_name: str) -> bool:
        """Determine if an NPC should react to a player action"""
        # NPCs are more likely to react to dramatic actions
        dramatic_actions = ["deal_damage", "give_item", "roll_saving_throw"]
        
        if tool_name in dramatic_actions:
            return random.random() < 0.7  # 70% chance to react to dramatic actions
        else:
            return random.random() < 0.2  # 20% chance to react to other actions
