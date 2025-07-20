import os
import streamlit as st
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from sqlalchemy import create_engine

from core.llm_service import LLMService
from core.orchestrator import WardenOrchestrator
from core.world_generator import WorldGenerator
from database.database import init_engine, get_db, dispose_engine
from database.models import GameEntity, Base, MapPoint
from core.rag_service import RAGService
from ui.character_creation_view import render_character_creation_view
from ui.main_view import render_main_view
from ui.sidebar_view import render_sidebar


ADVENTURES_DIR = "adventures"


def initialize_services():
    """Initializes and caches the core services for an active game."""
    if "rag_service" not in st.session_state:
        with next(get_db()) as db:
            st.session_state.rag_service = RAGService(db)
            st.session_state.rag_service.load_adventure_log()
            st.toast("Memory Engrams Loaded.")

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


def create_database_and_schema(db_path: str):
    """Creates a new database file, applies the schema, and stamps it with Alembic."""
    dispose_engine()  # Ensure no lingering connections
    if os.path.exists(db_path):
        # This should not happen in the new flow, but as a safeguard
        st.error(f"Database already exists at {db_path}. Cannot create a new one.")
        return

    # Create the new database and schema
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    engine.dispose()

    # Stamp the new database with the latest Alembic revision
    alembic_cfg = AlembicConfig("alembic.ini")
    # We need to tell Alembic where the database is
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    alembic_command.stamp(alembic_cfg, "head")
    st.toast("New world created and sealed with magic.")


def show_launcher():
    """Displays the main game launcher screen."""
    st.title("Cairn Solo AI Warden")
    st.write("Your journey begins here. Choose your path.")

    st.subheader("New Adventure")
    new_adventure_name = st.text_input("Enter a name for your new adventure:")
    if st.button("Create New Game", use_container_width=True):
        if not new_adventure_name:
            st.warning("Please enter a name for your adventure.")
        else:
            adventure_file = f"{new_adventure_name.strip().replace(' ', '_')}.db"
            db_path = os.path.join(ADVENTURES_DIR, adventure_file)

            if os.path.exists(db_path):
                st.error(
                    f"An adventure named '{new_adventure_name}' already exists. "
                    "Please choose a different name."
                )
            else:
                # 1. Create and stamp the new database
                create_database_and_schema(db_path)

                # 2. Initialize the engine for this new database
                init_engine(db_path)
                st.session_state["active_db_path"] = db_path

                # 3. Generate world and character
                with next(get_db()) as db:
                    # WorldGenerator will be fully implemented in Task 11
                    world_generator = WorldGenerator(db)
                    world_generator.generate_new_world()

                    # Create the character
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
                        attacks='[{"name": "Rusty Sword", "damage": "1d8"}]',
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
                            # Add a hostile wolf for the first encounter
                            wolf = GameEntity(
                                name="Starving Wolf",
                                entity_type="Monster",
                                hp=4,
                                max_hp=4,
                                strength=6,
                                max_strength=6,
                                dexterity=12,
                                max_dexterity=12,
                                willpower=6,
                                max_willpower=6,
                                is_hostile=True,
                                attacks='[{"name": "Bite", "damage": "1d6"}]',
                                current_location_id=start_map_point.default_location.id,
                            )
                            db.add(wolf)

                    db.add(new_character)
                    db.commit()
                    db.refresh(new_character)
                    st.session_state["character_id"] = new_character.id

                # 4. Set game state and rerun
                st.session_state["game_active"] = True
                st.rerun()

    st.divider()
    st.subheader("Load Existing Adventure")

    if not os.path.exists(ADVENTURES_DIR):
        os.makedirs(ADVENTURES_DIR)

    adventures = [f for f in os.listdir(ADVENTURES_DIR) if f.endswith(".db")]

    if not adventures:
        st.info("No existing adventures found.")
    else:
        for adventure_db in adventures:
            adventure_name = os.path.splitext(adventure_db)[0].replace("_", " ")
            if st.button(f"Load '{adventure_name}'", use_container_width=True):
                db_path = os.path.join(ADVENTURES_DIR, adventure_db)

                # 1. Initialize engine for the selected database
                init_engine(db_path)
                st.session_state["active_db_path"] = db_path

                # 2. Find the active character in the loaded game
                with next(get_db()) as db:
                    character = (
                        db.query(GameEntity)
                        .filter(
                            GameEntity.entity_type == "Character",
                            GameEntity.is_retired == False, # noqa: E712
                        )
                        .first()
                    )

                    if character:
                        st.session_state["character_id"] = character.id
                        st.session_state["game_active"] = True
                        st.rerun()
                    else:
                        st.error(
                            "Could not find an active character in this adventure. "
                            "The file may be corrupted or empty."
                        )


def show_main_layout():
    """Displays the main game interface."""
    initialize_services()
    with next(get_db()) as db:
        character = (
            db.query(GameEntity)
            .filter(GameEntity.id == st.session_state["character_id"])
            .first()
        )

        if not character or character.is_retired:
            st.title("Your story has ended... for now.")
            st.write(
                "The torch has been passed. A new adventurer may rise to continue the legacy."
            )
            if st.button("Create New Character", use_container_width=True):
                # Create a new character in the same world
                new_character = GameEntity(
                    name="New Adventurer",
                    entity_type="Character",
                    hp=3,
                    max_hp=3,
                    strength=10,
                    max_strength=10,
                    dexterity=10,
                    max_dexterity=10,
                    willpower=10,
                    max_willpower=10,
                    attacks='[{"name": "Simple Dagger", "damage": "1d4"}]',
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
                st.rerun()
            return

        render_sidebar(character, db)
        render_main_view(db)


def main():
    """Main application entry point."""
    st.set_page_config(page_title="Cairn Solo AI Warden", layout="wide")

    if st.session_state.get("character_creation_active"):
        with next(get_db()) as db:
            render_character_creation_view(db)
        return

    # The main logic is now a simple switch based on the "game_active" state
    if st.session_state.get("game_active"):
        if "active_db_path" in st.session_state:
            init_engine(st.session_state["active_db_path"])
            show_main_layout()
        else:
            # This case should not happen, but as a safeguard
            st.error("Game is active but no database path is set. Returning to menu.")
            st.session_state["game_active"] = False
            st.rerun()
    else:
        show_launcher()


if __name__ == "__main__":
    main()
