import streamlit as st
from database.database import get_db
from database.models import GameEntity

def show_welcome_screen():
    """Displays the initial screen for starting or loading a game."""
    st.title("Cairn Solo AI Warden")
    st.write("Welcome, adventurer. Your journey begins here.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Game", use_container_width=True):
            with next(get_db()) as db:
                # For now, create a simple default character
                new_character = GameEntity(
                    name="Grimgar",
                    entity_type="Character",
                    hp=3, max_hp=6, strength=12, dexterity=10, willpower=8
                )
                db.add(new_character)
                db.commit()
                db.refresh(new_character)
                st.session_state['character_id'] = new_character.id

            st.session_state['game_active'] = True
            st.rerun()
            
    with col2:
        if st.button("Load Game", use_container_width=True):
            # This will be implemented later
            st.warning("Load Game functionality not yet implemented.")

def show_main_layout():
    """Displays the main game interface."""
    with next(get_db()) as db:
        character = db.query(GameEntity).filter(GameEntity.id == st.session_state['character_id']).first()

    if not character:
        st.error("Character not found. Please start a new game.")
        st.session_state['game_active'] = False
        st.rerun()
        return

    # --- SIDEBAR (Player Hub & Tools) ---
    with st.sidebar:
        st.title("Player Hub")
        
        # VitalsView
        st.header(character.name)
        vitals_container = st.container(border=True)
        col1, col2, col3, col4 = vitals_container.columns(4)
        col1.metric("HP", f"{character.hp}/{character.max_hp}")
        col2.metric("STR", character.strength)
        col3.metric("DEX", character.dexterity)
        col4.metric("WIL", character.willpower)
        
        # InventoryView Placeholder
        st.header("Inventory")
        st.container(border=True).write("10-slot grid")

        # Game Controls
        st.header("Game Controls")
        st.button("Save Game", use_container_width=True)
        if st.button("Exit to Main Menu", use_container_width=True):
            st.session_state['game_active'] = False
            del st.session_state['character_id']
            st.rerun()

    # --- MAIN AREA (Session & Context) ---
    st.title("Adventure Log")

    # Context View Placeholder
    with st.container(border=True):
        st.subheader("Context View")
        # MapView Placeholder
        st.write("**Map View**")
        st.container(border=True).write("Graphviz map will be here.")
        
    # Game Log Placeholder
    st.subheader("Session View")
    with st.container(border=True, height=400):
        st.write("The game log will appear here...")

    # User Input
    st.chat_input("What do you do?")


def main():
    """Main application entry point."""
    st.set_page_config(page_title="Cairn Solo AI Warden", layout="wide")

    # If game_active is explicitly set to False, show welcome screen (e.g., user clicked "Exit")
    if st.session_state.get('game_active') is False:
        show_welcome_screen()
        return

    # If game is already active in session, show main layout
    if st.session_state.get('game_active'):
        show_main_layout()
        return

    # On first load, check if a character exists in the DB to auto-load the game
    try:
        with next(get_db()) as db:
            character = db.query(GameEntity).filter(GameEntity.entity_type == "Character", GameEntity.is_retired == False).first()
            if character:
                st.session_state['game_active'] = True
                st.session_state['character_id'] = character.id
                st.rerun()
            else:
                show_welcome_screen()
    except Exception as e:
        # This can happen if the DB doesn't exist or the schema is wrong
        # In either case, we show the welcome screen to start fresh.
        show_welcome_screen()

if __name__ == "__main__":
    main()