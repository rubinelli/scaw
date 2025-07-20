"""
This module provides a service for generating a complete, randomized character.
"""

import random
from .oracles import (
    PHYSIQUE,
    SKIN,
    HAIR,
    FACE,
    SPEECH,
    CLOTHING,
    VIRTUE,
    VICE,
    BONDS,
    OMENS,
    BACKGROUNDS,
)


class CharacterGenerator:
    """A service for generating a complete, randomized character."""

    def _d6(self):
        return random.randint(1, 6)

    def _d10(self):
        return random.randint(1, 10)

    def _d20(self):
        return random.randint(1, 20)

    def _3d6(self):
        return self._d6() + self._d6() + self._d6()

    def generate_character(self) -> dict:
        """Generates a complete, randomized character.

        Returns:
            A dictionary representing the character sheet.
        """
        background_roll = self._d20()
        background = BACKGROUNDS[background_roll]

        character_sheet = {
            "name": random.choice(background["names"]),
            "background": background["name"],
            "strength": self._3d6(),
            "dexterity": self._3d6(),
            "willpower": self._3d6(),
            "hp": self._d6(),
            "age": self._d20() + self._d20() + 10,
            "physique": PHYSIQUE[self._d10()],
            "skin": SKIN[self._d10()],
            "hair": HAIR[self._d10()],
            "face": FACE[self._d10()],
            "speech": SPEECH[self._d10()],
            "clothing": CLOTHING[self._d10()],
            "virtue": VIRTUE[self._d10()],
            "vice": VICE[self._d10()],
            "bond": BONDS[self._d20()],
            "omen": OMENS[self._d20()],
            "starting_gear": background["starting_gear"],
            "background_specific": {},
        }

        for key, value in background.items():
            if key not in ["name", "starting_gear", "names"]:
                roll_result = value[self._d6()]
                character_sheet["background_specific"][key] = roll_result["description"]
                character_sheet["starting_gear"].extend(roll_result["items"])

        return character_sheet
