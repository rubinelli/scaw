import streamlit as st
from sqlalchemy.orm import Session
from database.models import GameEntity


def render_sidebar(character: GameEntity, db: Session):
    """Renders the entire sidebar with player info, inventory, and controls."""
    with st.sidebar:
        st.title("Player Hub")
        st.header(character.name)

        _render_vitals(character)
        _render_inventory(character, db)
        _render_game_controls()


def _render_vitals(character: GameEntity):
    """Renders the character's vitals section."""
    vitals_container = st.container(border=True)
    col1, col2 = vitals_container.columns(2)
    col1.metric("HP", f"{character.hp}/{character.max_hp}")
    col2.metric("Fatigue", character.fatigue)
    vitals_container.divider()
    vitals_container.metric("STR", f"{character.strength}/{character.max_strength}")
    vitals_container.metric("DEX", f"{character.dexterity}/{character.max_dexterity}")
    vitals_container.metric("WIL", f"{character.willpower}/{character.max_willpower}")


def _render_inventory(character: GameEntity, db: Session):
    """Renders the character's 10-slot inventory grid."""
    st.header("Inventory")
    inventory_container = st.container(border=True)

    # Create a list of items, with None for empty slots
    inventory_slots = [None] * 10
    for i, item in enumerate(character.items):
        if i < 10:
            inventory_slots[i] = item

    # Display the 10-slot grid
    for i, item in enumerate(inventory_slots):
        col1, col2 = inventory_container.columns([3, 1])
        slot_text = f"{i + 1}. "
        if item:
            slot_text += f"{item.name} (x{item.quantity})"
            # Use a unique key for each button
            if col2.button("Drop", key=f"drop_{item.id}", use_container_width=True):
                st.session_state.orchestrator.handle_player_input(
                    f"drop {item.name}", db
                )
                st.rerun()
        else:
            slot_text += "Empty"
        col1.write(slot_text)


def _render_game_controls():
    """Renders the game control buttons."""
    st.header("Game Controls")
    st.button("Save Game (autosaved)", use_container_width=True, disabled=True)
    if st.button("Exit to Main Menu", use_container_width=True):
        st.session_state["game_active"] = False
        # Clean up session state before going to launcher
        for key in ["character_id", "active_db_path", "orchestrator"]:
            if key in st.session_state:
                del st.session_state[key]
        from database.database import dispose_engine

        dispose_engine()
        st.rerun()
