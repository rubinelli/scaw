# Development Plan: Solo Cairn AI Warden (Critique & Refinement)

> **Original Author:** marcos
> **Revised:** 2025-07-19
> **Critique:** This is a strong, well-structured plan. The primary refinement suggested here is to **prioritize the "Game Management" feature (Task 12)**. This is a foundational architectural change that impacts how the database is accessed. Implementing it *before* other features that interact with the database (like inventory and world generation) will prevent significant refactoring and streamline development.

This revised plan re-orders the tasks for efficiency and renumbers them sequentially for clarity.

# Initial Design
---

## Phase 1: Foundation (The Core MVP)

**Goal:** Implement the minimum viable product. A functional application where a player can create a character within a persistent, named adventure, manage their inventory, and engage in the core gameplay loops.

---


### **Task 1: Project Setup and Streamlit Initialization** [Status: Done]
- **Priority:** high
- **Dependencies:** []
- **Description:** Initialize the Python project, set up Streamlit, and establish the basic project structure.

### **Task 2: Setup Alembic for Database Migrations** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Initialize and configure Alembic to manage database schema changes.

### **Task 3: Implement Core Database Schema** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Define and create the complete SQLite database schema using the SQLAlchemy ORM.

### **Task 4: Develop Basic UI Layout** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Build the main UI layout using Streamlit components, including the welcome screen and main game view with placeholders.

### **Task 5: Implement Core Character Vitals** [Status: Done]
- **Priority:** high
- **Dependencies:** [2, 3]
- **Description:** Implement the `VitalsView` in the sidebar and the basic character creation flow.

### **Task 6: Implement Game Log & User Input** [Status: Done]
- **Priority:** high
- **Dependencies:** [2, 3]
- **Description:** Implement the `GameLogView` to display database entries and the `UserInputBar` to capture player text.

### **Task 7: Implement Simple LLM Service** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Implement the `LLMService` with a single, default provider (Gemini) and test its connectivity.

### **Task 8: Develop Core Warden Orchestrator & Tool-Calling Loop** [Status: Done]
- **Priority:** high
- **Dependencies:** [5, 6]
- **Description:** Build the core `WardenOrchestrator` to interpret natural language input and use a tool-calling LLM to execute game actions.
- **Subtasks:**
    - **8.1: Create WardenOrchestrator Class:** Define the main class structure.
    - **8.2: Define "World Tools":** Create a set of simple, powerful functions in `src/core/world_tools.py` that represent fundamental game actions (e.g., `roll_dice`, `deal_damage`, `move_character`).
    - **8.3: Implement Tool-Calling Loop:** The orchestrator will pass the player's natural language input and the available "World Tools" to the `LLMService`.
    - **8.4: Implement Tool Execution:** The orchestrator will receive the LLM's chosen tool and arguments, execute the corresponding Python function, and update the game state.
    - **8.5: Synthesize Narrative:** The orchestrator will take the result of the executed tool and use the `LLMService` to generate a narrative description of the outcome for the player.
- **Test Strategy:** Write unit tests for each "World Tool". Write integration tests to verify that natural language commands (e.g., "I attack the goblin") correctly trigger the appropriate tool-calling sequence and state changes.

### **Task 9: Implement Core Combat & Healing Loop** [Status: Done]
- **Priority:** high
- **Dependencies:** [2, 7]
- **Description:** Implement the fundamental mechanics for combat, healing, and character death.
- **Subtasks:**
    - **9.1: Enhance `GameEntity` Model:** Add `scars` (String) and `is_hostile` (Boolean) fields to the model in `src/database/models.py`.
    - **9.2: Create Database Migration:** Generate and apply a new Alembic migration to update the database schema with the new fields.
    - **9.3: Update `deal_damage` Logic:** Modify the `deal_damage` tool in `src/core/world_tools.py` to handle the "Scar" mechanic when HP hits 0, apply damage to STR only after HP is depleted, and mark entities as `is_retired` at 0 STR without deleting them.
    - **9.4: Implement Healing Tools:** Create a `rest` tool to restore HP to max and a placeholder `make_camp` tool in `src/core/world_tools.py`.
    - **9.5: Implement NPC Reaction Logic:** In `src/core/orchestrator.py`, after a player action, query for hostile NPCs at the location and trigger a counter-attack using the `deal_damage` tool.
    - **9.6: Synthesize Turn Narrative:** Consolidate the results of the player's action and all NPC counter-attacks into a single narrative response using the `LLMService`.
- **Test Strategy:** Create a test scenario with a player and a monster. Verify that using `/attack` correctly reduces the monster's HP and STR, triggers a Scar, and eventually marks it as retired. Test that `rest` restores player HP. Test that a hostile NPC automatically counter-attacks.

---
### **Task 10: Implement Robust Game Management (New, Load, Save)**
- **Priority:** critical
- **Dependencies:** [3]
- **Description:** Refactor the application to support multiple, named adventures instead of a single hardcoded database file. This involves creating a main menu/launcher to manage game slots and abstracting database connections.
- **Subtasks:**
    - **10.1: Abstract Database Path:** Remove the hardcoded `DB_FILE` constant. All database connections will instead use a path stored in Streamlit's session state (e.g., `st.session_state['active_db_path']`).
    - **10.2: Create Adventure Storage:** Establish a dedicated directory (e.g., `scaw/adventures/`) to store all adventure database files (`.db`).
    - **10.3: Implement Game Launcher UI:** Rework the `show_welcome_screen` to act as a full game launcher. It will scan the `adventures/` directory and list all existing `.db` files for the user to choose from.
    - **10.4: Implement "Load Game" Flow:** When a user selects an existing adventure, store its file path in `st.session_state['active_db_path']` and transition to the main game view.
    - **10.5: Implement "New Game" Flow:** The launcher will include a "New Adventure" button and a text input. On creation, it will generate a new, named database file, run the `WorldSeedGenerator` (from Task 11), populate the initial character, and set the new path as the `active_db_path`.
    - **10.6: Implement "Save Game" (Placeholder):** The "Save Game" button will be a placeholder, as all changes are committed directly to the active `.db` file.
- **Test Strategy:** Verify that creating a new game does not overwrite an existing one. Test loading different games sequentially, ensuring the state is correctly isolated.

### **Task 11: Implement World Seed Generator**
- **Priority:** high
- **Dependencies:** [10]
- **Description:** Create the `WorldSeedGenerator` module to pre-generate the entire map graph and save it to the database for a new adventure. This should be called during the "New Game" flow.

### **Task 12: Implement Core Inventory Management**
- **Priority:** high
- **Dependencies:** [3, 5, 8]
- **Description:** Replace the inventory placeholder with a functional UI and the logic to manage items.
- **Subtasks:**
    - **12.1: Create `InventoryView` Component:** Build a UI function to display the character's `Item` records in the sidebar.
    - **12.2: Implement `drop <item>` Handler:** Create the orchestrator logic to handle dropping items.
    - **12.3: Implement `use <item>` Handler:** Create a placeholder handler for using consumable items.
- **Test Strategy:** Create a character with items. Verify they display correctly. Test dropping and using items.

### **Task 13: Implement Basic Map Display**
- **Priority:** high
- **Dependencies:** [4, 11]
- **Description:** Implement the `MapView` to render a non-interactive, informational graph of the world based on the generated seed.

---

## Phase 2: Enrichment (Dynamic World & Player Agency)

**Goal:** Build upon the core loop to make the world feel dynamic and reactive. This phase introduces procedural systems and gives the player more meaningful choices.

---

### **Task 14: Enhance Map System with "Known World" Logic**
- **Priority:** high
- **Dependencies:** [13]
- **Description:** Enhance the `MapView` to handle all four statuses (`hidden`, `rumored`, `known`, `explored`). Implement the logic for discovering locations and paths.

### **Task 15: Implement Procedural Narrative Framework (Oracles)**
- **Priority:** high
- **Dependencies:** [8]
- **Description:** Integrate the Cairn 2E oracles (e.g., Wilderness Events). The `WardenOrchestrator` will trigger these oracles, and the results will be used by the LLM to synthesize narrative.

### **Task 16: Implement Full Character Inventory**
- **Priority:** high
- **Dependencies:** [12]
- **Description:** Implement the full `InventoryView` with its 10-slot grid. Implement the mechanic for when Fatigue forces an item drop.

### **Task 17: Implement Saving Throw Mechanic**
- **Priority:** high
- **Dependencies:** [6, 8]
- **Description:** Implement a "[Click to Roll]" button in the `GameLogView` and the corresponding backend logic to prompt for and resolve saving throws.

### **Task 18: Implement Legacy Play**
- **Priority:** medium
- **Dependencies:** [10]
- **Description:** Add a UI flow for creating a new character within the *currently loaded* adventure after the previous character has been retired.

---

## Phase 3: Immersion (Advanced Features)

**Goal:** Add the final layer of advanced features that create deep immersion, improve AI quality, and provide long-term replayability.

---

### **Task 19: Integrate RAG Context Store (LangChain & ChromaDB)**
- **Priority:** high
- **Dependencies:** [8]
- **Description:** Integrate LangChain and ChromaDB to provide the AI Warden with a long-term, searchable memory of the narrative log, improving context and consistency. The RAG index should be built from the active adventure's database.

### **Task 20: Implement Multi-Provider LLM Service & Settings UI**
- **Priority:** medium
- **Dependencies:** [7]
- **Description:** Extend the `LLMService` to support multiple backends (OpenAI, Gemini, Local). Create a `SettingsView` UI for users to configure their provider and API keys.

### **Task 21: Implement Player Agency Tools (Codex & Oracles)**
- **Priority:** low
- **Dependencies:** [4, 3]
- **Description:** Implement a player-facing `CodexView` for searching discovered lore and an `OraclePanelView` for manual dice rolling.

### **Task 22: Implement Generative Imaging**
- **Priority:** low
- **Dependencies:** [4]
- **Description:** Implement an `ImageGenerationService` and a UI button to allow players to generate images for characters, scenes, or items.

### **Task 23: Implement Post-Generation Parsing**
- **Priority:** medium
- **Dependencies:** [14, 19]
- **Description:** Implement logic for the Warden to parse its own output to identify and act on mechanically significant information (e.g., automatically marking a location as `rumored`).

---

## Phase 4: Advanced Character Creation

**Goal:** Overhaul the character creation process to fully align with the Cairn 2E Player's Guide, providing a dynamic, randomized, and interactive experience for the player.

---

### **Task 24: Data Extraction & Modeling for Character Creation**
- **Priority:** Critical
- **Dependencies:** [P1-Task-3]
- **Description:** Extract all character creation tables (Backgrounds, Traits, Bonds, Omens) from `Cairn_2E_Players_Guide.md` and model them as structured data in `src/core/oracles.py`. This will centralize the data for easy access by the generation logic.
- **Subtasks:**
    - **24.1: Model Core Trait Tables:** Create new dictionaries in `oracles.py` for all d10 Trait tables: `PHYSIQUE`, `SKIN`, `HAIR`, `FACE`, `SPEECH`, `CLOTHING`, `VIRTUE`, and `VICE`.
    - **24.2: Model Bonds and Omens:** Create new d20 dictionaries in `oracles.py` for `BONDS` and `OMENS`.
    - **24.3: Model Backgrounds:** Create a comprehensive `BACKGROUNDS` dictionary in `oracles.py`. Each of the 20 backgrounds will be a key, and its value will be a dictionary containing its starting gear, a list of names, and its unique sub-tables for random generation.
- **Test Strategy:** N/A (This is primarily a data entry and modeling task).

### **Task 25: Develop Character Generation Service**
- **Priority:** Critical
- **Dependencies:** [24]
- **Description:** Create a `CharacterGenerator` service in a new file, `src/core/character_generator.py`. This service will encapsulate all the logic for creating a complete, randomized character according to the rules, without directly interacting with the UI or database.
- **Subtasks:**
    - **25.1: Implement the `CharacterGenerator` Class:** This class will use the newly modeled oracle tables.
    - **25.2: Create `generate_character()` Method:** This core method will perform all the necessary rolls:
        - Roll 3d6 for STR, DEX, and WIL.
        - Roll 1d6 for HP.
        - Roll on all Trait, Bond, and Omen tables.
        - Roll for Age (2d20+10).
        - Randomly select a Background and process its specific tables for starting gear and abilities.
        - Return a single, structured "character sheet" object containing all the generated data.
- **Test Strategy:** Write unit tests for the `CharacterGenerator` service. Verify that the generated character object contains all required fields (stats, traits, items, etc.) and that the attribute and HP values fall within their expected ranges (e.g., STR between 3 and 18).

### **Task 26: Implement Interactive Character Creation UI**
- **Priority:** High
- **Dependencies:** [25]
- **Description:** Create a new UI screen, defined in `src/ui/character_creation_view.py`, that allows the player to generate and re-roll a character until they are satisfied.
- **Subtasks:**
    - **26.1: Create the `render_character_creation_view` function:** This function will manage the layout of the new screen.
    - **26.2: Design the Character Sheet Display:** The UI will clearly present all the generated character information: name, attributes, HP, traits, bond, omen, and the complete list of starting items and abilities from their background. This data will be temporarily stored in `st.session_state`.
    - **26.3: Implement "Generate / Re-roll" Button:** This button will call the `CharacterGenerator` service to create a new character sheet and update the display.
    - **26.4: Implement "Accept & Begin" Button:** This button will finalize the character creation process, triggering the logic to save the character to the database.
- **Test Strategy:** Manual UI testing to ensure the character sheet displays correctly and that the "Re-roll" functionality works as expected.

### **Task 27: Integrate New Creation Flow into Application**
- **Priority:** High
- **Dependencies:** [26]
- **Description:** Update the main application logic in `src/app.py` to direct the user to the new character creation screen after starting a new adventure.
- **Subtasks:**
    - **27.1: Modify the "New Game" Flow:** In the `show_launcher()` function, after a new adventure database is created, set a session state flag (e.g., `st.session_state['character_creation_active'] = True`) to signal that character creation should begin.
    - **27.2: Update Application Router:** In the `main()` function, add logic to check for the `character_creation_active` flag and call `render_character_creation_view()` when it is true.
    - **27.3: Implement Character Persistence:** The "Accept & Begin" button in the new UI will be responsible for taking the character data from session state, creating the `GameEntity` and associated `Item` records in the database, and then transitioning the application to the main game view.
- **Test Strategy:** Conduct an end-to-end test of the complete "New Game" -> "Create Character" -> "Begin Adventure" user flow to ensure seamless integration.

---

## Future Considerations

Items from the PRD's "Out of Scope" section will be considered after the completion of these three phases.
- Multiplayer functionality.
- VTT Integration.
- Mobile/Responsive UI.
- Support for third-party supplements.

---

## Phase 5: Generative World Enrichment

**Goal:** Overhaul the world generation process to create richer, more detailed, and narratively compelling environments. This involves using the LLM to expand simple points of interest into multi-location areas with evocative descriptions and populated contents.

---

### **Task 28: Enhance Database for Richer World Data**
- **Priority:** Critical
- **Dependencies:** [3]
- **Description:** Modify the database schema to support more detailed and LLM-generated world information.
- **Subtasks:**
    - **28.1: Add `summary` to `MapPoint`:** Add a `summary` text field to the `MapPoint` model to store an LLM-generated overview of the area.
    - **28.2: Add `is_entry_point` to `Location`:** Add an `is_entry_point` boolean field to the `Location` model to designate it as the primary entry, replacing the old `default_location` foreign key.
    - **28.3: Create Database Migration:** Generate and apply a new Alembic migration for these schema changes.

### **Task 29: Overhaul World Generator for LLM-driven Enrichment**
- **Priority:** Critical
- **Dependencies:** [7, 11, 28]
- **Description:** Refactor the `WorldGenerator` to use the `LLMService` to transform basic procedural outputs into rich, multi-location points of interest.
- **Subtasks:**
    - **29.1: Inject `LLMService`:** The `WorldGenerator` will be initialized with an `LLMService` instance.
    - **29.2: Implement Two-Phase Generation:** The process will be split. First, generate the mechanical details of a `MapPoint` (type, name). Second, use a new method to enrich it.
    - **29.3: Create `_enrich_map_point_with_llm` Method:** This new private method will construct a detailed prompt asking the LLM to act as a game master. The LLM will return a JSON object containing a `summary` for the `MapPoint`, a list of 2-4 interconnected `Locations` (with `name`, `description`, and suggested `contents`), and a simple connection map.
    - **29.4: Implement LLM Output Processing:** The `WorldGenerator` will parse the LLM's JSON response to create the `Location` and `LocationConnection` records in the database, populating them with the generated descriptions and contents (as `GameEntity` or `Item` records). One location will be marked as the `is_entry_point`.

### **Task 30: Adapt Application to New World Structure**
- **Priority:** High
- **Dependencies:** [8, 29]
- **Description:** Update other parts of the application to correctly use the new, richer world structure.
- **Subtasks:**
    - **30.1: Update Orchestrator:** Modify the `WardenOrchestrator` to use the `MapPoint.summary` for context and to place new characters at the `Location` marked `is_entry_point` within the starting `MapPoint`.
    - **30.2: Adjust Character Placement:** Ensure the new character flow correctly identifies and uses the `is_entry_point` location when a new game begins.

---

# Major Update #1: Tension & Choice-Driven Gameplay

**Goal:** Transform the game from a functional but static experience into an engaging, choice-driven adventure with meaningful time pressure and dynamic NPCs that create emergent narrative moments.

---

## Phase 1: Foundation - Tension Engine

### **Task 31: Implement Tension Tracking System**
- **Priority:** Critical
- **Dependencies:** [3]
- **Description:** Create the core database schema and services to track tension events with escalating consequences and multiple resolution paths.
- **Subtasks:**
    - **31.1: Add Tension Database Models:** Create `TensionEvent` and `ResolutionCondition` models in `src/database/models.py`
    - **31.2: Create Database Migration:** Generate and apply Alembic migration for new tables
    - **31.3: Implement `ConditionTracker` Service:** Create service to monitor game state changes and detect when resolution conditions are met
    - **31.4: Hook into World Tools:** Add condition checking to existing world_tools functions (deal_damage, add_item_to_inventory, move_character, etc.)
- **Test Strategy:** Unit tests for ConditionTracker service. Integration tests to verify condition detection works with existing world tools.

### **Task 32: Enhanced LLM Persona & NPC AI**
- **Priority:** High  
- **Dependencies:** [7, 8]
- **Description:** Improve the AI Warden's narrative voice and implement dynamic NPC behavior that creates engaging interactions.
- **Subtasks:**
    - **32.1: Enhanced System Prompts:** Update SYSTEM_PROMPT in llm_service.py with richer sensory description guidelines and NPC behavior instructions
    - **32.2: Dynamic NPC Disposition System:** Implement logic for NPCs to change their attitude based on player actions
    - **32.3: Combat Initiation System:** Allow hostile NPCs to initiate combat and neutral NPCs to become hostile
    - **32.4: Proactive NPC Behavior:** Add system for NPCs to occasionally act independently
    - **32.5: Enhanced Orchestrator Integration:** Update orchestrator.py to use new NPC reaction system
- **Test Strategy:** Manual testing of NPC reactions to various player actions. Unit tests for disposition change logic.

---

## Phase 2: Immediate Engagement Boost

### **Task 33: Omen-Driven Tension Events**
- **Priority:** High
- **Dependencies:** [31, 32]
- **Description:** Replace simple character creation with a system that generates urgent, escalating problems based on the character's Omen.
- **Subtasks:**
    - **33.1: Modify Character Creation:** Update character creation flow to generate tension events from Omens
    - **33.2: Multiple Resolution Paths:** Ensure each tension event has 2-3 different ways to resolve it
    - **33.3: Escalation System:** Implement automatic severity increases over time
    - **33.4: LLM Integration:** Use LLM to generate compelling tension event descriptions and consequences
- **Test Strategy:** Create characters with different Omens and verify appropriate tension events are generated. Test escalation timing.

### **Task 34: Populated Starting Hub**
- **Priority:** High
- **Dependencies:** [33]
- **Description:** Ensure every new adventure begins in a populated settlement with NPCs who have urgent needs that become tension events.
- **Subtasks:**
    - **34.1: Settlement Generation Logic:** Modify WorldGenerator to guarantee first MapPoint is always a settlement
    - **34.2: NPC Population:** Create 3-4 non-hostile NPCs with backstories and urgent problems
    - **34.3: Urgent Problems as Tension Events:** Convert NPC needs into tension events with deadlines
    - **34.4: Character Placement:** Ensure player always starts at settlement entry point
- **Test Strategy:** Generate multiple new adventures and verify each starts in a populated settlement with active tension events.

---

## Phase 3: Dynamic World Response

### **Task 35: Consequence Propagation System**
- **Priority:** Medium
- **Dependencies:** [34]
- **Description:** Make failed tension events permanently change the world state, creating lasting consequences for player choices.
- **Subtasks:**
    - **35.1: Failure Consequences:** Implement logic for what happens when tension events fail (NPCs die, locations change status, new opportunities emerge)
    - **35.2: Success Rewards:** Create positive consequences for resolving tension events (better prices, new areas accessible, faction standing)
    - **35.3: Cascading Events:** Implement system where resolving one tension event can trigger new ones
    - **35.4: World State Persistence:** Ensure consequences are saved and affect future interactions
- **Test Strategy:** Test scenarios where tension events fail and succeed, verify world state changes persist.

### **Task 36: Enhanced Information & Rumor System**
- **Priority:** Medium
- **Dependencies:** [35]
- **Description:** Give players more control over which tensions to engage with through an information gathering system.
- **Subtasks:**
    - **36.1: NPC Dialogue Enhancement:** NPCs provide hints about multiple brewing tensions
    - **36.2: Hidden Tension Discovery:** Some tension events only become visible through investigation
    - **36.3: Player Choice Integration:** Allow players to choose which rumors to investigate
    - **36.4: Information as Resource:** Make what the player knows affect available resolution paths
- **Test Strategy:** Manual testing of information gathering mechanics. Verify hidden tensions are discoverable through NPC interaction.

---

## Phase 4: Polish & Integration

### **Task 37: UI/UX Refinements**
- **Priority:** Low
- **Dependencies:** [36]
- **Description:** Improve the user interface to better communicate tension events, deadlines, and consequences.
- **Subtasks:**
    - **37.1: Tension Event Display:** Add UI elements to show active tension events and their deadlines
    - **37.2: Enhanced Feedback:** Ensure tension escalations and resolutions are clearly communicated in the game log
    - **37.3: Visual Cues:** Add visual indicators for NPC disposition changes and urgent situations
    - **37.4: Quest Log Integration:** Create simple quest log to track active tension events
- **Test Strategy:** Manual UI testing to ensure all tension system elements are clearly communicated to the player.

### **Task 38: System Integration & Testing**
- **Priority:** High
- **Dependencies:** [37]
- **Description:** Comprehensive testing and refinement of the complete tension system.
- **Subtasks:**
    - **38.1: End-to-End Testing:** Test complete new game -> tension events -> resolution -> consequences flow
    - **38.2: Performance Optimization:** Ensure condition checking doesn't impact game performance
    - **38.3: Edge Case Handling:** Test and fix edge cases in tension event system
    - **38.4: Documentation Updates:** Update player manual and PRD to reflect new features
- **Test Strategy:** Comprehensive integration testing of all tension system components working together.

---

## Success Metrics for Major Update #1

- **Immediate Engagement:** Every new character starts with 2-3 urgent, escalating problems
- **Meaningful Choices:** Each tension event has multiple resolution paths with different consequences  
- **Time Pressure:** Deadlines force players to prioritize and make difficult decisions
- **Dynamic NPCs:** NPCs change their behavior based on player actions and world events
- **Lasting Impact:** Player choices create permanent changes to the world state
- **Replayability:** Different resolution choices lead to significantly different world states

This update transforms the game from a sandbox with AI narrator into an urgent, choice-driven adventure where every decision matters and the world responds dynamically to player actions.
