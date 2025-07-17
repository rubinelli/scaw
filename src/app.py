import os
import streamlit as st
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from sqlalchemy import create_engine

from core.llm_service import LLMService
from core.orchestrator import WardenOrchestrator
from core.world_generator import WorldGenerator
from database.database import get_db, dispose_engine
from database.models import GameEntity, LogEntry, Base, MapPoint

DB_FILE = "active_game.db"


def initialize_services():
    """Initializes and caches the core services."""
    if "llm_service" not in st.session_state:
        try:
            st.session_state.llm_service = LLMService()
            st.toast("LLM Service Initialized.")
        except ValueError as e:
            st.error(f"Failed to initialize LLM Service: {e}")
            st.stop()
    if "orchestrator" not in st.session_state:
        with next(get_db()) as db:
            st.session_state.orchestrator = WardenOrchestrator(
                st.session_state.llm_service, db
            )


def create_new_database():
    """Wipes and creates a fresh database with the current schema and stamps it."""
    dispose_engine()
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Base.metadata.create_all(engine)
    engine.dispose()
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_command.stamp(alembic_cfg, "head")
    st.toast("New world created.")


def show_welcome_screen():
    """Displays the initial screen for starting or loading a game."""
    st.title("Cairn Solo AI Warden")
    st.write("Welcome, adventurer. Your journey begins here.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Game", use_container_width=True):
            create_new_database()
            with next(get_db()) as db:
                world_generator = WorldGenerator(db)
                world_generator.generate_new_world()

                new_character = GameEntity(
                    name="Grimgar",
                    entity_type="Character",
                    hp=3,
                    max_hp=3,
                    strength=12,
                    max_strength=12,
                    dexterity=10,
                    max_dexterity=10,
                    willpower=8,
                    max_willpower=8,
                )
                start_map_point = (
                    db.query(MapPoint).filter(MapPoint.status == "explored").first()
                )
                if start_map_point:
                    new_character.current_map_point_id = start_map_point.id
                    if start_map_point.default_location:
                        new_character.current_location_id = (
                            start_map_point.default_location.id
                        )

                db.add(new_character)
                db.commit()
                db.refresh(new_character)
                st.session_state["character_id"] = new_character.id

            st.session_state["game_active"] = True
            st.rerun()

    with col2:
        if st.button("Load Game", use_container_width=True):
            st.warning("Load Game functionality not yet implemented.")


def show_main_layout():
    """Displays the main game interface."""
    initialize_services()
    with next(get_db()) as db:
        character = (
            db.query(GameEntity)
            .filter(GameEntity.id == st.session_state["character_id"])
            .first()
        )
        log_entries = db.query(LogEntry).order_by(LogEntry.created_at.asc()).all()

        if not character:
            st.error("Character not found. Please start a new game.")
            st.session_state["game_active"] = False
            st.rerun()
            return

        # --- SIDEBAR ---
        with st.sidebar:
            st.title("Player Hub")
            st.header(character.name)
            vitals_container = st.container(border=True)
            col1, col2 = vitals_container.columns(2)
            col1.metric("HP", f"{character.hp}/{character.max_hp}")
            col2.metric("Fatigue", character.fatigue)
            vitals_container.divider()
            vitals_container.metric(
                "STR", f"{character.strength}/{character.max_strength}"
            )
            vitals_container.metric(
                "DEX", f"{character.dexterity}/{character.max_dexterity}"
            )
            vitals_container.metric(
                "WIL", f"{character.willpower}/{character.max_willpower}"
            )
            st.header("Inventory")
            st.container(border=True).write("10-slot grid")
            st.header("Game Controls")
            st.button("Save Game", use_container_width=True)
            if st.button("Exit to Main Menu", use_container_width=True):
                st.session_state["game_active"] = False
                del st.session_state["character_id"]
                st.rerun()

        # --- MAIN AREA ---
        st.title("Adventure Log")
        with st.container(border=True):
            st.subheader("Context View")
            st.write("**Map View**")
            st.container(border=True).write("Graphviz map will be here.")

        st.subheader("Session View")
        log_container = st.container(border=True, height=400)
        for entry in log_entries:
            with log_container.chat_message(name=entry.source.lower()):
                st.markdown(entry.content)

        if prompt := st.chat_input("What do you do?"):
            with next(get_db()) as db:
                st.session_state.orchestrator.handle_player_input(prompt, db)
            st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(page_title="Cairn Solo AI Warden", layout="wide")

    if st.session_state.get("game_active") is False:
        show_welcome_screen()
        return

    if st.session_state.get("game_active"):
        show_main_layout()
        return

    try:
        with next(get_db()) as db:
            character = (
                db.query(GameEntity)
                .filter(
                    GameEntity.entity_type == "Character",
                    GameEntity.is_retired == False,  # noqa: E712
                )
                .first()
            )
            if character:
                st.session_state["game_active"] = True
                st.session_state["character_id"] = character.id
                show_main_layout()
                return
    except Exception:
        pass
    show_welcome_screen()


if __name__ == "__main__":
    main()
