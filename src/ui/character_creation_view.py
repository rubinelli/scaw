"""
This module provides the UI for the character creation screen.
"""

import streamlit as st
from core.character_generator import CharacterGenerator

from database.models import GameEntity, Item


def render_character_creation_view(db):
    """Renders the character creation screen."""
    st.title("Create Your Character")

    if "character_sheet" not in st.session_state:
        st.session_state.character_sheet = CharacterGenerator().generate_character()

    character_sheet = st.session_state.character_sheet

    col1, col2 = st.columns(2)

    with col1:
        st.header("Attributes")
        st.metric("Strength", character_sheet["strength"])
        st.metric("Dexterity", character_sheet["dexterity"])
        st.metric("Willpower", character_sheet["willpower"])
        st.metric("HP", character_sheet["hp"])
        st.metric("Age", character_sheet["age"])

        st.header("Traits")
        st.write(f"**Physique:** {character_sheet['physique']}")
        st.write(f"**Skin:** {character_sheet['skin']}")
        st.write(f"**Hair:** {character_sheet['hair']}")
        st.write(f"**Face:** {character_sheet['face']}")
        st.write(f"**Speech:** {character_sheet['speech']}")
        st.write(f"**Clothing:** {character_sheet['clothing']}")
        st.write(f"**Virtue:** {character_sheet['virtue']}")
        st.write(f"**Vice:** {character_sheet['vice']}")

    with col2:
        st.header(f"{character_sheet['name']} the {character_sheet['background']}")
        st.subheader("Bond")
        st.write(character_sheet["bond"])
        st.subheader("Omen")
        st.write(character_sheet["omen"])

        st.subheader("Starting Gear")
        for item in character_sheet["starting_gear"]:
            st.write(f"- {item}")

        st.subheader("Background Specific")
        for key, value in character_sheet["background_specific"].items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    st.divider()

    col1, col2 = st.columns(2)
    if col1.button("Generate / Re-roll Character", use_container_width=True):
        st.session_state.character_sheet = CharacterGenerator().generate_character()
        st.rerun()

    if col2.button("Accept & Begin Adventure", use_container_width=True):
        # Save the character to the database
        new_character = GameEntity(
            name=character_sheet["name"],
            entity_type="Character",
            hp=character_sheet["hp"],
            max_hp=character_sheet["hp"],
            strength=character_sheet["strength"],
            max_strength=character_sheet["strength"],
            dexterity=character_sheet["dexterity"],
            max_dexterity=character_sheet["dexterity"],
            willpower=character_sheet["willpower"],
            max_willpower=character_sheet["willpower"],
            age=character_sheet["age"],
            description=f"{character_sheet['physique']}, {character_sheet['skin']}, {character_sheet['hair']}, {character_sheet['face']}, {character_sheet['speech']}, {character_sheet['clothing']}",
            background=character_sheet["background"],
            bond=character_sheet["bond"],
            omen=character_sheet["omen"],
        )
        db.add(new_character)
        db.commit()

        for item_name in character_sheet["starting_gear"]:
            item = Item(name=item_name, owner=new_character)
            db.add(item)
        db.commit()

        st.session_state["character_id"] = new_character.id
        st.session_state["character_creation_active"] = False
        st.session_state["game_active"] = True
        st.rerun()
