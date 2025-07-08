# Development Plan: Solo Cairn AI Warden (Phased Delivery)

> **Updated:** 2025-07-06

This document outlines a phased, iterative development plan for the Solo Cairn AI Warden project, designed for a solo developer. The goal is to deliver a playable core experience first, then build upon it with more advanced features.

---

## Phase 1: The Core Experience (MVP)

**Goal:** Implement the minimum viable product. A functional application where a player can create a character, see their immediate surroundings on a map, interact with the world via text, and get a response from a single, default LLM.

---

### **Task 1: Project Setup and Streamlit Initialization** [Status: pending]
- **Priority:** high
- **Dependencies:** []
- **Description:** Initialize the Python project, set up Streamlit, and establish the basic project structure.

### **Task 1.5: Setup Alembic for Database Migrations** [Status: pending]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Initialize and configure Alembic to manage database schema changes. This is critical for ensuring that user save files (`.db`) from older versions of the application can be automatically upgraded to work with newer versions.
- **Subtasks:**
    - **1.5.1: Initialize Alembic:** Run `alembic init` to create the configuration files and versions directory.
    - **1.5.2: Configure Alembic:** Edit `alembic.ini` and `env.py` to correctly target the SQLAlchemy models and database connection.
- **Test Strategy:** Create an initial Alembic revision and confirm it can be applied to an empty database.

### **Task 2: Implement Core Database Schema** [Status: pending]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Define and create the complete SQLite database schema using the SQLAlchemy ORM. Each database file represents a single, self-contained adventure.
- **Subtasks:**
    - **2.1: Define All ORM Models:** Create Python classes for all data models (`GameEntity`, `Item`, `LogEntry`, `MapPoint`, `Location`, `Path`) inheriting from a SQLAlchemy declarative base.
    - **2.2: Define All Model Fields:** Add all fields to each model with correct types as per the PRD. The `Adventure` table is no longer needed.
    - **2.3: Define Relationships:** Implement foreign keys and relationships between the models.
    - **2.4: Create Database Schema:** Write a script that uses `metadata.create_all(engine)` to generate the database file and all tables.
- **Test Strategy:** Inspect the generated `.db` file to ensure all tables, columns, and constraints are created correctly and that no `Adventure` table exists.

### **Task 3: Develop Basic UI Layout** [Status: pending]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Build the main UI layout using Streamlit components. The application should start with a welcome screen that presents "New Game" and "Load Game" options. Once a game is active, the UI will switch to the main three-part layout with placeholders.
- **Subtasks:**
    - **3.1: Implement Initial State Check:** Create logic to check if a game is active in the `st.session_state`.
    - **3.2: Implement Welcome Screen:** If no game is active, display the New/Load UI.
    - **3.3: Implement Main Layout:** If a game is active, display the main layout with a sidebar and main area, containing placeholders for the `VitalsView`, `InventoryView`, `MapView`, and `GameLogView`.
- **Test Strategy:** Run the app (`streamlit run app.py`) and verify the welcome screen appears first. After simulating a game load, verify the main layout renders correctly.

### **Task 4: Implement Core Character Vitals** [Status: pending]
- **Priority:** high
- **Dependencies:** [2, 3]
- **Description:** Implement the `VitalsView` in the sidebar to display character stats (HP, STR, DEX, WIL). Implement a basic character creation flow to set these initial stats. The full inventory view will be a placeholder.
- **Subtasks:**
    - **4.1: Create VitalsView Component:** Build a function that uses `st.metric` or `st.markdown` to display character stats in the sidebar.
    - **4.2: Create Basic Character Creation Logic:** Implement a function that creates a new `GameEntity` in the database with default or rolled stats.
    - **4.3: Link VitalsView to Data:** Use Streamlit's session state (`st.session_state`) to store and retrieve the active character's data from the database and display it in the `VitalsView`.
    - **4.4: Create InventoryView Placeholder:** Create an empty placeholder for the `InventoryView` in the sidebar.
- **Test Strategy:** Test the character creation flow. Verify that the created character's stats are correctly stored in the session state and displayed in the sidebar.

### **Task 5: Implement Game Log & User Input** [Status: pending]
- **Priority:** high
- **Dependencies:** [2, 3]
- **Description:** Implement the `GameLogView` to display `LogEntry` data from the database and the `UserInputBar` to capture player text input.
- **Subtasks:**
    - **5.1: Create GameLogView and UserInputBar Components:** Use `st.chat_message` in a loop to render the game log and `st.chat_input` for the user input bar.
    - **5.2: Implement Log Fetching:** Add logic to fetch `LogEntry` records from the database, storing them in the session state.
    - **5.3: Render Log Data:** Iterate through the log entries in the session state and display them.
    - **5.4: Implement Input Handling:** The `st.chat_input` will return the user's text. When text is submitted, save it to the database as a new `LogEntry` and rerun the app to update the log.
- **Test Strategy:** Manually add log entries to the database and verify they display correctly. Test submitting text and confirm it appears in the log on the next app run.

### **Task 6: Implement Simple LLM Service** [Status: pending]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Implement the `LLMService` with a single, default provider (Gemini). The goal is to have a working connection to one LLM, without the complexity of multiple providers or a settings UI yet.
- **Subtasks:**
    - **6.1: Define LLMService Interface:** Create a base class or a simple function signature for `generate_response(prompt)`.
    - **6.2: Implement Gemini Backend:** Create a class or function that implements the interface using the `google-generativeai` library.
    - **6.3: Manage API Key:** Load the Gemini API key from a GOOGLE_API_KEY environment variable.
- **Test Strategy:** Write a simple test that sends a "Hello" prompt to the Gemini service and verifies a non-empty response is received. We should have one version as unit test mocking the SDK, and another test working as integration test, that checks for the API KEY and skips if not found in the environment.

### **Task 7: Develop Core Warden Orchestrator** [Status: pending]
- **Priority:** high
- **Dependencies:** [5, 6]
- **Description:** Build the core `WardenOrchestrator` to receive player input, parse it to distinguish between natural language and slash commands, send it to the `LLMService`, and log the conversation.
- **Subtasks:**
    - **7.1: Create WardenOrchestrator Class:** Define the main class structure.
    - **7.2: Implement Input Processing & Parsing:** Create the method to receive input from the UI. This method must include logic to detect if the input starts with `/`. If it does, parse the command and its arguments; otherwise, treat it as natural language.
    - **7.3: Integrate LLMService:** In the input processor, call the `LLMService` with the player's input (or a prompt derived from a slash command).
    - **7.4: Integrate Logging:** Log the player's input and the LLM's response as new `LogEntry` records in the database.
- **Test Strategy:** Send both natural language and slash command inputs from the UI. Verify the Orchestrator correctly parses commands and that the full conversation is saved to the database and displayed in the `GameLogView`.

### **Task 8: Implement World Seed Generator** [Status: pending]
- **Priority:** high
- **Dependencies:** [2]
- **Description:** Create the `WorldSeedGenerator` module. This is critical for creating the initial, cohesive world state that the player will explore. It will pre-generate the entire map graph and save it to the database.
- **Subtasks:**
    - **8.1: Implement Faction Generation:** Generate 1-3 factions using the PRD tables and save them to the database.
    - **8.2: Implement Topography and POI Generation:** Run the "Die Drop" procedures to create terrain regions and POIs, saving them as `MapPoint` records with coordinates.
    - **8.3: Implement Path Generation:** Connect the generated `MapPoint` nodes with `Path` records, calculating `watches` based on distance and terrain.
    - **8.4: Set Initial Map Status:** Set the starting POI to `explored`, its immediate neighbors and paths to `known`, and all other map elements to `hidden`.
- **Test Strategy:** Run the generator. Inspect the database to verify a complete, interconnected world graph has been created and that initial statuses are set correctly.

### **Task 9: Implement Basic Map Display** [Status: pending]
- **Priority:** high
- **Dependencies:** [2, 3, 8]
- **Description:** Implement the `MapView` to render a non-interactive, informational graph of the pre-generated world using Graphviz. It will only display `known` and `explored` nodes and paths, with a clear marker for the player's current location.
- **Subtasks:**
    - **9.1: Fetch Known/Explored Data:** Query the database for all `MapPoint` and `Path` records with a status of `known` or `explored`.
    - **9.2: Render Static Map:** Use the `st.graphviz_chart` component to display the fetched nodes and paths. Add a distinct style for the node representing the player's `current_map_point_id`.
    - **9.3: Implement `/travel` Command:** The sole mechanism for movement will be the `/travel <location_name>` command, handled by the Warden Orchestrator. This command will update the character's `current_map_point_id` in the database and rerun the app, which will cause the map to re-render with the updated player position.
- **Test Strategy:** Verify the map correctly displays the initial known/explored area and the player's starting location. Test the `/travel` command and confirm the player marker moves to the correct location on the map after the app reruns.

### **Task 10: Implement Basic Game Management (New, Save, Load)** [Status: pending]
- **Priority:** high
- **Dependencies:** [8, 4.2, 1.5]
- **Description:** Implement the core game management flow based on manipulating a single SQLite database file per adventure, with robust support for schema migrations.
- **Subtasks:**
    - **10.1: Implement "New Game":** Create a button that triggers a workflow: 1. Deletes any existing `active_game.db`. 2. Creates a new `active_game.db` using `metadata.create_all()`. 3. Programmatically "stamps" the new DB with the latest Alembic revision (`alembic stamp head`). 4. Calls the `WorldSeedGenerator` and character creation logic. 5. Reruns the Streamlit app.
    - **10.2: Implement "Save Game":** Create a function that makes a copy of the `active_game.db`. Use `st.download_button` in the UI to offer this copy to the user for download.
    - **10.3: Implement "Load Game":** Use `st.file_uploader` to allow the user to upload a `.db` save file. On upload: 1. Validate the file. 2. Programmatically run `alembic upgrade head` on the uploaded file to apply any necessary schema migrations. 3. Replace the `active_game.db` with the migrated file. 4. Rerun the app.
- **Test Strategy:** Test the full New-Save-Load loop. Create a v1 save file, add a v2 migration, and ensure the v1 file is automatically upgraded on load.

---

## Phase 2: Dynamic World & Player Agency

**Goal:** Build upon the core loop to make the world feel dynamic and reactive. This phase introduces the key procedural systems from Cairn and gives the player more control and meaningful choices.

---

### **Task 11: Implement Full "Known World" Map System** [Status: pending]
- **Priority:** high
- **Dependencies:** [P1-Task-9]
- **Description:** Enhance the `MapView` to handle all four statuses (`hidden`, `rumored`, `known`, `explored`). Implement the UI and backend logic for discovering rumored locations and revealing hidden paths.

### **Task 12: Implement Procedural Narrative Framework (Oracles)** [Status: pending]
- **Priority:** high
- **Dependencies:** [P1-Task-7]
- **Description:** Implement the full Procedural Narrative Framework, integrating the Cairn 2E oracles (Wilderness Events, Dungeon Events, etc.). The `WardenOrchestrator` will now trigger these oracles, and the results will be used to synthesize narrative with the LLM.

### **Task 13: Implement Full Character Sheet & Inventory** [Status: pending]
- **Priority:** high
- **Dependencies:** [P1-Task-4]
- **Description:** Implement the full `InventoryView` with its 10-slot grid. Implement the "[Click to Drop]" mechanic for when Fatigue forces an item drop.

### **Task 14: Implement Saving Throw Mechanic** [Status: pending]
- **Priority:** high
- **Dependencies:** [P1-Task-5, P1-Task-7]
- **Description:** Implement the "[Click to Roll]" button in the `GameLogView` and the corresponding backend logic in the `WardenOrchestrator` to prompt for and resolve saving throws.

### **Task 15: Implement Legacy Play** [Status: pending]
- **Priority:** medium
- **Dependencies:** [P1-Task-10]
- **Description:** Implement the "Legacy Play" feature. This involves adding a UI flow for creating a new character within the *currently loaded* adventure database after the previous character has been marked as `is_retired`.

---

## Phase 3: Advanced Features & Immersion

**Goal:** Add the final layer of advanced features that create deep immersion, improve AI quality, and provide long-term replayability.

---

### **Task 16: Integrate RAG Context Store (Cognee)** [Status: medium]
- **Priority:** high
- **Dependencies:** [P1-Task-7]
- **Description:** Integrate Cognee to provide the AI Warden with a long-term, searchable memory of the narrative log, improving context and consistency in its responses.

### **Task 17: Implement Multi-Provider LLM Service & Settings UI** [Status: pending]
- **Priority:** medium
- **Dependencies:** [P1-Task-6]
- **Description:** Extend the `LLMService` to support multiple backends (OpenAI, Gemini, Local). Create the `SettingsView` UI for users to configure their chosen provider, API keys, and endpoints.

### **Task 18: Implement Player Agency Tools (Codex & Oracles)** [Status: pending]
- **Priority:** low
- **Dependencies:** [P1-Task-3, P1-Task-2]
- **Description:** Implement the player-facing `CodexView` for searching discovered lore and the `OraclePanelView` for manual dice rolling.

### **Task 19: Implement Generative Imaging** [Status: pending]
- **Priority:** low
- **Dependencies:** [P1-Task-3]
- **Description:** Implement the `ImageGenerationService` and the UI button to allow players to generate images for characters, scenes, or items.

### **Task 20: Implement Post-Generation Parsing** [Status: pending]
- **Priority:** medium
- **Dependencies:** [P2-Task-11, P3-Task-16]
- **Description:** Implement the logic for the Warden to parse its own output to identify and act on mechanically significant information (e.g., automatically marking a location as `rumored`).

---

## Future Considerations

Items from the PRD's "Out of Scope" section will be considered after the completion of these three phases.
- Multiplayer functionality.
- VTT Integration.
- Mobile/Responsive UI.
- Support for third-party supplements.
