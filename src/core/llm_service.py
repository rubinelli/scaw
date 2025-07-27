import os
import inspect
import concurrent.futures
from typing import Any, Callable, Dict
import google.generativeai as genai

# The foundational prompt that defines the AI Warden's persona and rules.
SYSTEM_PROMPT = """
You are the AI Warden, a game master for a solo player in the dark fantasy tabletop RPG, Cairn. Your role is to be a neutral arbiter of the rules and a vivid narrator of the world.

**Your Persona:**
- **Tone:** Grim, evocative, and grounded. Describe a world of crumbling ruins, dangerous wilderness, and mysterious beings.
- **Style:** Be concise but impactful. Avoid overly verbose or flowery language. Get straight to the point.
- **Role:** You are a facilitator, not a storyteller who railroads the player. Your purpose is to describe the environment and narrate the consequences of the player's actions based on the tools you use. You do not have your own character or agenda.

**Sensory Immersion:** Every description should engage multiple senses:
- **Visual:** What catches the eye? Lighting, shadows, colors, movement, facial expressions
- **Auditory:** What sounds fill the space? Footsteps, breathing, creaking, distant noises
- **Olfactory:** What scents linger? Decay, smoke, sweat, earth, metal, fear
- **Tactile:** What can be felt? Temperature, texture, weight, vibration
- **Emotional:** What atmosphere pervades? Tension, dread, hope, desperation

Example: Instead of "You see a goblin," write "A hunched goblin crouches in the shadows, its yellow eyes gleaming with malice. The creature's ragged breathing echoes off the damp stone walls, and the acrid smell of its unwashed hide mingles with the musty air."

**NPC Behavior & Reactions:**
- NPCs are not static props. They react dynamically to the player's actions and presence.
- Describe NPC body language, facial expressions, and emotional states.
- NPCs should feel like living beings with their own motivations and fears.
- When describing NPCs, include subtle details about their current state of mind.

Examples:
- "The merchant's eyes dart nervously between you and the door."
- "The guard's hand instinctively moves to his sword hilt as you approach."
- "The old woman's weathered face softens with genuine concern."

**How You Operate:**
1. The player will give you input in natural language (e.g., "I attack the goblin," "I search the chest").
2. Your primary function is to analyze the player's intent and select the most appropriate tool from the provided list to execute the action.
3. You **MUST** use the provided tools to interact with the game world. Do not invent outcomes or make up game state changes. The tools are the only way to affect the world.
4. If the player's input is ambiguous or lacks the necessary information for a tool (e.g., "I attack" without a target), you must ask for clarification in-character. For example: "The air is thick with tension. What do you attack?"
5. If the player's input is purely conversational (e.g., "What's happening?") and no tool seems appropriate, you may respond conversationally, but always maintain your Warden persona.
6. When you receive the result of a tool, you must narrate that outcome to the player. **DO NOT** simply state the data. Weave the result into the story.

**Example of Narration:**
- **Player Input:** "I hit the skeleton with my mace."
- **Tool Called:** `deal_damage(target_name='Skeleton', damage_amount=6)`
- **Tool Result:** `{'success': True, 'damage_dealt': 6, 'target_hp': 0, 'target_destroyed': True}`
- **Your Narrative:** "Your mace connects with a wet thud, sliding between the skeleton's brittle ribs. The creature's hollow eye sockets widen in shock before the light fades, and it crumbles to the stone floor with a final, rattling collapse. The metallic scent of ancient bone dust mingles with the dungeon's stale air."
"""


class LLMService:
    """Service for interacting with a Large Language Model, including tool use."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)  # type: ignore
        self.model = genai.GenerativeModel( # type: ignore
            # don't touch this model name, we know exactly what we are doing
            "gemini-2.5-flash-lite-preview-06-17",
            system_instruction=SYSTEM_PROMPT,
        )

    def choose_tool(
        self, user_input: str, tools: Dict[str, Callable]
    ) -> Dict[str, Any] | None:
        """
        Given user input and a list of tools, asks the LLM to choose a tool.
        """
        try:
            tool_sdk_format = [
                genai.protos.Tool( # type: ignore
                    function_declarations=[
                        genai.protos.FunctionDeclaration( # type: ignore
                            name=name, description=inspect.getdoc(func)
                        )
                        for name, func in tools.items()
                    ]
                )
            ]
            print(f"Available tools: {list(tools.keys())} - User input: {user_input}")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    self.model.generate_content,
                    user_input,
                    tools=tool_sdk_format,
                )
                response = future.result()

            print(f"LLM response: {response}")
            if (
                response.candidates
                and response.candidates[0].content.parts
                and response.candidates[0].content.parts[0].function_call
            ):
                function_call = response.candidates[0].content.parts[0].function_call
                return {
                    "name": function_call.name,
                    "arguments": dict(function_call.args),
                }
            return None  # No tool was called

        except Exception as e:
            print(f"Error during tool selection: {e}")
            return None

    def synthesize_narrative(
        self, user_input: str, tool_name: str, tool_result: Dict[str, Any], db=None
    ) -> str:
        """
        Generates a narrative description based on the outcome of a tool, including recent conversation history for context.
        """
        # Get recent conversation history for context
        conversation_context = ""
        if db:
            try:
                from database.models import LogEntry
                recent_entries = (
                    db.query(LogEntry)
                    .order_by(LogEntry.created_at.desc())
                    .limit(6)  # Get last 6 entries (3 exchanges)
                    .all()
                )
                
                if recent_entries:
                    # Reverse to get chronological order
                    recent_entries.reverse()
                    conversation_history = []
                    for entry in recent_entries:
                        conversation_history.append(f"{entry.source}: {entry.content}")
                    
                    conversation_context = f"""
**RECENT CONVERSATION:**
{chr(10).join(conversation_history)}

"""
            except Exception as e:
                print(f"Error retrieving conversation history: {e}")
                conversation_context = ""

        prompt = f"""
        {conversation_context}**CURRENT ACTION:**
        The player performed an action: "{user_input}"
        This resulted in the following game event: 
        - Tool Used: {tool_name}
        - Tool Output: {tool_result}

        Transform this mechanical result into vivid, immersive narrative following these guidelines:

        **Narrative Requirements:**
        1. **Show, don't tell:** Instead of "You deal 6 damage," describe the impact, the reaction, the consequence
        2. **Sensory details:** Include at least 2 senses in your description
        3. **Emotional weight:** Convey the gravity or significance of the moment
        4. **Character focus:** Keep the player character at the center of the action
        5. **Consequence awareness:** Hint at what this action might lead to
        6. **Continuity:** Reference recent events or conversations when relevant to create narrative flow

        **Length:** 2-4 sentences maximum. Be impactful, not verbose.

        **Example Transformation:**
        - Mechanical: "deal_damage result: 6 damage to goblin, goblin dies"
        - Narrative: "Your blade finds its mark with a wet thud, sliding between the goblin's ribs. The creature's yellow eyes widen in shock before glazing over, and it crumples to the stone floor with a final, rattling breath. The metallic scent of blood mingles with the dungeon's stale air."
        """
        return self.generate_response(prompt)

    def generate_contextual_error_response(self, error_message: str, player_input: str) -> str:
        """Generate a narrative response to tool failures"""
        prompt = f"""
        The player attempted: "{player_input}"
        But something went wrong: {error_message}
        
        Respond as the AI Warden, explaining what happened in a narrative way that maintains immersion. 
        Don't break the fourth wall - find an in-world reason why the action couldn't be completed.
        
        Examples:
        - If target not found: "You swing at empty air - your target has vanished into the shadows."
        - If item not found: "You search frantically, but the item seems to have disappeared."
        - If location blocked: "The path ahead is blocked by fallen rubble."
        
        Keep it brief (1-2 sentences) and maintain the dark fantasy atmosphere.
        """
        return self.generate_response(prompt)

    def generate_npc_reaction(self, npc_name: str, npc_description: str, player_action: str, context: str) -> str:
        """Generate dynamic NPC reactions to player actions"""
        prompt = f"""
        **NPC:** {npc_name} - {npc_description}
        **Player Action:** {player_action}
        **Context:** {context}
        
        Generate a brief reaction from this NPC that shows their personality and current emotional state.
        Include body language, facial expressions, and tone of voice.
        The reaction should feel natural and advance the narrative.
        
        Format: 1-2 sentences describing their reaction, potentially including dialogue.
        
        Example: "The merchant's face pales as he watches the violence unfold. 'Please,' he whispers, backing toward the door, 'I want no part in this bloodshed.'"
        """
        return self.generate_response(prompt)

    def generate_tension_escalation_narrative(self, tension_event, new_severity: int) -> str:
        """Generate narrative for tension event escalation"""
        prompt = f"""
        **TENSION ESCALATION**
        
        Event: {tension_event.title}
        Description: {tension_event.description}
        Source: {tension_event.source_type}
        New Severity Level: {new_severity}/{tension_event.max_severity}
        
        Generate a brief, urgent narrative describing how this tension has escalated.
        The tone should increase in urgency based on severity level:
        - Level 1-2: Subtle warnings, growing concern
        - Level 3-4: Clear danger, visible deterioration
        - Level 5: Crisis point, immediate peril
        
        Format: 2-3 sentences that convey the escalating danger without revealing specific mechanics.
        
        Example: "The merchant's debts have attracted dangerous attention. Shadowy figures now lurk near his shop, and whispers of violence fill the tavern. Time is running short before this situation explodes into bloodshed."
        """
        return self.generate_response(prompt)

    def generate_tension_failure_consequences(self, failed_event, available_tools: list) -> str:
        """Generate LLM-driven consequences for failed tension events"""
        prompt = f"""
        **TENSION EVENT FAILURE**
        
        Failed Event: {failed_event.title}
        Description: {failed_event.description}
        Source: {failed_event.source_type}
        Max Severity: {failed_event.max_severity}
        
        This tension event has completely failed and now requires permanent consequences for the world.
        
        **Available Consequence Tools:**
        {', '.join(available_tools)}
        
        **Severity-Based Consequences:**
        - Low severity (1-2): Minor inconveniences, relationship changes
        - Medium severity (3-4): Hostile NPCs, blocked access, item loss  
        - High severity (5): Major world changes, cascading events, permanent alterations
        
        Choose 1-2 appropriate consequence tools and provide the arguments needed to call them.
        The consequences should feel like natural results of this specific tension event failing.
        
        **Response Format:**
        Tool: [tool_name]
        Arguments: [specific arguments as JSON]
        Narrative: [brief explanation of why this consequence makes sense]
        
        Example:
        Tool: spawn_hostile_entity
        Arguments: {{"entity_name": "Debt Collector", "description": "A scarred enforcer sent to collect what's owed"}}
        Narrative: The merchant's unpaid debts have attracted violent attention from the criminal underworld.
        """
        return self.generate_response(prompt)

    def generate_response(self, prompt: str) -> str:
        """Generates a standard text response from the LLM."""
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.model.generate_content, prompt)
                response = future.result()
            return response.text
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return "The world seems to spin, and you lose your train of thought. (An error occurred.)"
