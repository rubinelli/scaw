# Development Plan: Solo Cairn AI Warden (Phased Delivery)

> **Updated:** 2025-07-06

This document outlines a phased, iterative development plan for the Solo Cairn AI Warden project, designed for a solo developer. The goal is to deliver a playable core experience first, then build upon it with more advanced features.

---

## Phase 1: The Core Experience (MVP)

**Goal:** Implement the minimum viable product. A functional application where a player can create a character, manage their inventory, explore the world, and engage in the core gameplay loops of combat and healing.

---

### **Task 1: Project Setup and Streamlit Initialization** [Status: Done]
- **Priority:** high
- **Dependencies:** []
- **Description:** Initialize the Python project, set up Streamlit, and establish the basic project structure.

### **Task 1.5: Setup Alembic for Database Migrations** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Initialize and configure Alembic to manage database schema changes.

### **Task 2: Implement Core Database Schema** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Define and create the complete SQLite database schema using the SQLAlchemy ORM.

### **Task 3: Develop Basic UI Layout** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Build the main UI layout using Streamlit components, including the welcome screen and main game view with placeholders.

### **Task 4: Implement Core Character Vitals** [Status: Done]
- **Priority:** high
- **Dependencies:** [2, 3]
- **Description:** Implement the `VitalsView` in the sidebar and the basic character creation flow.

### **Task 5: Implement Game Log & User Input** [Status: Done]
- **Priority:** high
- **Dependencies:** [2, 3]
- **Description:** Implement the `GameLogView` to display database entries and the `UserInputBar` to capture player text.

### **Task 6: Implement Simple LLM Service** [Status: Done]
- **Priority:** high
- **Dependencies:** [1]
- **Description:** Implement the `LLMService` with a single, default provider (Gemini) and test its connectivity.

### **Task 7: Develop Core Warden Orchestrator & Tool-Calling Loop** [Status: WIP]
- **Priority:** high
- **Dependencies:** [5, 6]
- **Description:** Build the core `WardenOrchestrator` to interpret natural language input and use a tool-calling LLM to execute game actions.
- **Subtasks:**
    - **7.1: Create WardenOrchestrator Class:** Define the main class structure.
    - **7.2: Define "World Tools":** Create a set of simple, powerful functions in `src/core/world_tools.py` that represent fundamental game actions (e.g., `roll_dice`, `deal_damage`, `move_character`).
    - **7.3: Implement Tool-Calling Loop:** The orchestrator will pass the player's natural language input and the available "World Tools" to the `LLMService`.
    - **7.4: Implement Tool Execution:** The orchestrator will receive the LLM's chosen tool and arguments, execute the corresponding Python function, and update the game state.
    - **7.5: Synthesize Narrative:** The orchestrator will take the result of the executed tool and use the `LLMService` to generate a narrative description of the outcome for the player.
- **Test Strategy:** Write unit tests for each "World Tool". Write integration tests to verify that natural language commands (e.g., "I attack the goblin") correctly trigger the appropriate tool-calling sequence and state changes.

### **Task 8: Implement Core Combat & Healing Loop** [Status: pending]
- **Priority:** high
- **Dependencies:** [2, 7]
- **Description:** Implement the fundamental mechanics for combat, healing, and character death.
- **Subtasks:**
    - **8.1: Implement `/attack` Handler:** Create the orchestrator method to handle the `/attack` command, identify the target `GameEntity` in the database, and calculate damage.
    - **8.2: Implement Damage Application:** Create a utility function to apply damage to a `GameEntity`, first reducing HP, then STR. Include logic for the HP=0 "Scar" event.
    - **8.3: Implement Death Handling:** Add logic to check if an entity's STR is 0 or less after taking damage. If so, mark them as `is_retired` or remove them from the database.
    - **8.4: Implement `/rest` and `/makecamp` Handlers:** Create handlers that restore HP (rest) and handle fatigue/rations (makecamp, placeholder for now).
    - **8.5: Implement Basic NPC Response:** After a player action, have the orchestrator trigger a simple, rule-based counter-attack from any hostile NPCs in the scene.
- **Test Strategy:** Create a test scenario with a player and a monster. Verify that using `/attack` correctly reduces the monster's HP and STR, and eventually kills it. Test that `/rest` restores player HP.

### **Task 9: Implement Core Inventory Management** [Status: pending]
- **Priority:** high
- **Dependencies:** [2, 4, 7]
- **Description:** Replace the inventory placeholder with a functional UI and the logic to manage items.
- **Subtasks:**
    - **9.1: Create `InventoryView` Component:** Build a UI function that queries the database for the character's `Item` records and displays them in a grid in the sidebar.
    - **9.2: Implement `/drop <item>` Handler:** Create the orchestrator method to handle dropping items, removing the `Item` from the character's inventory in the database.
    - **9.3: Implement `/use <item>` Handler:** Create a placeholder handler that acknowledges the use of an item and removes it from inventory if it's a consumable.
- **Test Strategy:** Create a character with several items. Verify they display correctly. Use `/drop` and confirm the item is removed. Use `/use` on a consumable and confirm it is removed.

### **Task 10: Implement World Seed Generator** [Status: pending]
- **Priority:** high
- **Dependencies:** [2]
- **Description:** Create the `WorldSeedGenerator` module to pre-generate the entire map graph and save it to the database.

### **Task 11: Implement Basic Map Display** [Status: pending]
- **Priority:** high
- **Dependencies:** [2, 3, 10]
- **Description:** Implement the `MapView` to render a non-interactive, informational graph of the world.

### **Task 12: Implement Basic Game Management (New, Save, Load)** [Status: pending]
- **Priority:** high
- **Dependencies:** [10, 4.2, 1.5]
- **Description:** Implement the core game management flow based on manipulating a single SQLite database file per adventure, with robust support for schema migrations.

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
