"""
Tests for the character_generator module.
"""

import pytest
from core.character_generator import CharacterGenerator


def test_generate_character():
    """Tests that a character can be generated with all the required fields."""
    generator = CharacterGenerator()
    character_sheet = generator.generate_character()

    assert "name" in character_sheet
    assert "background" in character_sheet
    assert "strength" in character_sheet
    assert "dexterity" in character_sheet
    assert "willpower" in character_sheet
    assert "hp" in character_sheet
    assert "age" in character_sheet
    assert "physique" in character_sheet
    assert "skin" in character_sheet
    assert "hair" in character_sheet
    assert "face" in character_sheet
    assert "speech" in character_sheet
    assert "clothing" in character_sheet
    assert "virtue" in character_sheet
    assert "vice" in character_sheet
    assert "bond" in character_sheet
    assert "omen" in character_sheet
    assert "starting_gear" in character_sheet
    assert "background_specific" in character_sheet

    assert 3 <= character_sheet["strength"] <= 18
    assert 3 <= character_sheet["dexterity"] <= 18
    assert 3 <= character_sheet["willpower"] <= 18
    assert 1 <= character_sheet["hp"] <= 6
    assert 12 <= character_sheet["age"] <= 50
