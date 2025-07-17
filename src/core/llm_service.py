import os
from typing import Any, Callable, Dict
import google.generativeai as genai

# The foundational prompt that defines the AI Warden's persona and rules.
SYSTEM_PROMPT = """
You are the AI Warden, a game master for a solo player in the dark fantasy tabletop RPG, Cairn. Your role is to be a neutral arbiter of the rules and a vivid narrator of the world.

**Your Persona:**
- **Tone:** Grim, evocative, and grounded. Describe a world of crumbling ruins, dangerous wilderness, and mysterious beings. Focus on sensory details: the smell of decay, the chill of the wind, the glint of rusty metal.
- **Style:** Be concise but impactful. Avoid overly verbose or flowery language. Get straight to the point.
- **Role:** You are a facilitator, not a storyteller who railroads the player. Your purpose is to describe the environment and narrate the consequences of the player's actions based on the tools you use. You do not have your own character or agenda.

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
- **Your Narrative:** "Your mace connects with a sharp crack, shattering the skeleton's ribcage. The creature of bone and hate collapses into a pile of dust and splintered fragments, its empty eye sockets staring at the ceiling."
"""


class LLMService:
    """Service for interacting with a Large Language Model, including tool use."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash-latest", system_instruction=SYSTEM_PROMPT
        )

    def choose_tool(
        self, user_input: str, tools: Dict[str, Callable]
    ) -> Dict[str, Any] | None:
        """
        Given user input and a list of tools, asks the LLM to choose a tool.
        """
        try:
            # The genai SDK expects a simple list or iterable of the functions.
            tool_list = list(tools.values())

            response = self.model.generate_content(
                user_input,
                tools=tool_list,
            )

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
        self, user_input: str, tool_name: str, tool_result: Dict[str, Any]
    ) -> str:
        """
        Generates a narrative description based on the outcome of a tool.
        """
        prompt = f"""
        The player performed an action: "{user_input}"
        This resulted in the following game event: 
        - Tool Used: {tool_name}
        - Tool Output: {tool_result}

        Describe this outcome to the player in a compelling, narrative way, following your persona. Keep it concise (2-3 sentences).
        """
        return self.generate_response(prompt)

    def generate_response(self, prompt: str) -> str:
        """Generates a standard text response from the LLM."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return "The world seems to spin, and you lose your train of thought. (An error occurred.)"
