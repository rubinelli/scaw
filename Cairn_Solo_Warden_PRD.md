# Product Requirements Document: Solo Cairn AI Warden

**Version:** 1.2
**Date:** 2025-07-05

---

## 1. Vision & Overview

### 1.1. Product Vision
To create a comprehensive, immersive, and user-friendly desktop application that acts as a digital Warden for solo players of the Cairn 2E tabletop role-playing game. The application will leverage generative AI to interpret rules, create dynamic content, and manage game state, allowing the player to focus on their character and the unfolding story.

### 1.2. Project Summary
The Solo Cairn AI Warden is a Python application built with the Streamlit framework. It provides a complete suite of tools to play Cairn without a human game master. Key features include an AI-powered Warden that can use local or commercial LLMs, a pointcrawl map for exploration, a digital character sheet, a long-term memory system for campaign continuity, and generative imaging to bring the world to life.

### 1.3. Target Audience
*   Solo TTRPG players who enjoy the OSR (Old School Renaissance) and NSR (New School Revolution) styles of play.
*   Existing players of Cairn who want a streamlined, digital-first way to play solo.
*   TTRPG enthusiasts interested in exploring the potential of AI-assisted role-playing.

---

## 2. Core Features & Functionality

### 2.1. Game & Adventure Management
*   **As a player, I want to start a new adventure**, which creates a new, self-contained world state.
*   **As a player, I want to save my adventure progress** by downloading a single save file (`.db`) to my computer.
*   **As a player, I want to load a previous adventure** by uploading a save file, replacing the current game state with the loaded one.
*   **As a player, I want to create a new character in an existing world** after my previous character dies or retires, so that persistent world elements (discovered map points, faction states, key NPCs) are carried over (Legacy Play).

### 2.2. AI Warden & Procedural Narrative Framework
*   **As a player, I want to choose between different LLM providers** (Local via Ollama/LM Studio, Gemini, ChatGPT) so I can use the model that best fits my needs and budget.
*   **As a player, I want to configure my LLM settings** (API keys, local model endpoint) within the app.
*   **As a player, I want the AI Warden to operate within a Procedural Narrative Framework**, where its primary role is to synthesize the results of structured oracle rolls into rich, coherent descriptions. The underlying roll results will be visible in the log for transparency. This ensures the game remains mechanically faithful to Cairn.
*   **As a player, I want the AI Warden to use the specific Cairn 2E oracles and procedures**, including multi-roll tables for deep, emergent results:
    *   **Adventure Site Generation:** Generating sites using the full `Dungeon Seed`, `Creator`, and `Purpose` tables to create unique locations.
    *   **Gameplay Procedures:** Automatically rolling on `Dungeon Events` and `Wilderness Events` tables, and using the `Reactions` table for NPCs.
*   **As a player, I want the AI Warden to roleplay NPCs, describe locations, and adjudicate outcomes** based on the rules and the established game state.
*   **As a player, I want to interact with the Warden through a natural language interface**, allowing me to describe my actions in plain English (e.g., "I ask the farmer about the ruins," "I attack the goblin with my sword," "I try to buy a sword").
*   **As a player, I want to be prompted by the Warden when a save is required**, and then be able to **click a button in the UI to initiate the roll**, giving me a sense of ownership over the outcome. The result will then be displayed narratively.

### 2.3. Character Sheet
*   **As a player, I want a digital character sheet** that displays my character's name, stats (HP, Strength, Dexterity, Willpower), `Fatigue`, Background, Bond, and any Omens.
*   **As a player, I want the option to accept my initial stat rolls or re-roll/manually edit them** for flexible character creation.
*   **As a player, I want to manage my character's inventory**, with the UI clearly showing the 10-slot limit and distinguishing the first four "comfortably carried" slots.
*   **As a player, I want the character sheet to be automatically updated** when events like taking damage, finding treasure, or adding `Fatigue` occur.
*   **As a player, I want to be prompted when Fatigue forces me to drop an item**, and be presented with a **clear UI (e.g., a "[Click to Drop]" button next to each item in the inventory)** to make a quick, decisive choice.

### 2.4. The "Known World" Pointcrawl Map
*   **As a player, I want to start a new adventure with a pre-generated, cohesive world map**, created using the full *Cairn Warden's Guide* procedures, to ensure the world feels alive and logically consistent.
*   **As a player, I want the map to be revealed progressively through a "fog of war"**, where locations and paths can have one of four statuses: `hidden`, `rumored`, `known`, or `explored`.
*   **As a player, I want to uncover `rumored` locations** by talking to NPCs, finding clues, or through wilderness events, which adds a question mark or faint icon to my map, creating a hook for future exploration.
*   **As a player, I want `rumored` or `hidden` locations to become `known`** when I discover a direct path to them, causing them to appear as solid, but unvisited, icons on the map.
*   **As a player, I want a `known` location to become `explored` only when I physically travel to it**, which fully reveals its details and allows me to add notes.
*   **As a player, I want the travel time in `Watches` to be displayed on each path**, automatically calculated during world generation based on distance and terrain.
*   **As a player, I want the ability to toggle a hex grid overlay** for an alternative view.

### 2.5. Player Agency & Tools
*   **As a player, I want explicit control over time management** via a `/rest` or `/makecamp` command, which advances `Watches`, triggers healing, and consumes rations.
*   **As a player, I want access to a player-facing Oracle Panel**, allowing me to roll on any game table myself for inspiration or to generate content.
*   **As a player, I want a structured and searchable in-game Codex** to keep track of discovered lore, locations, NPCs, and factions.

### 2.6. Dual-Component Memory Architecture
*   **As a player, I want the application to maintain world consistency** using a dual-component memory system.
    *   **State Database (SQLite Save File):** The entire game state is stored in a single SQLite (`.db`) file. This file *is* the save file, which the user can download and upload to manage persistence. It is the single source of truth for all structured, mutable game state (character stats, NPC status, inventory, map points, narrative log).
    *   **Context Store (RAG):** An indexed, searchable store of the unstructured narrative log. This index is treated as a temporary cache, rebuilt in memory from the `LogEntry` table in the SQLite file each time an adventure is loaded.

### 2.7. Image Generation
*   **As a player, I want the ability to generate an image for a character, scene, or item** based on the AI Warden's description, to enhance immersion.

---

## 3. Technical Requirements

### 3.1. Technology Stack
*   **Application Framework:** Python with [Streamlit](https://streamlit.io/)
*   **Package Management/Virtual Env:** [uv](https://github.com/astral-sh/uv)
*   **Context Store/RAG:** [LangChain](https://python.langchain.com/) with [ChromaDB](https://www.trychroma.com/)
*   **State Database:** SQLite.

### 3.2. Architecture
*   **World Seed Generator:** On starting a new adventure, the application will algorithmically pre-generate a complete and cohesive region. It will first establish a thematic foundation (regional culture, factions) and then generate a pointcrawl graph of nodes (POIs, Landmarks) with spatial coordinates. Nodes will be fully detailed using the *Warden's Guide* tables, and paths will be created to connect them logically, with travel times calculated based on distance and terrain. This entire world state is stored in the database.
*   **"Known World" Manager:** This module manages the player's view of the pre-generated map. It tracks the four-state status (`hidden`, `rumored`, `known`, `explored`) for every node and path, revealing them to the player based on in-game actions and discoveries.
*   **Warden Orchestrator:** The AI Warden will be architected as an orchestrator that parses player input, calls discrete, pluggable modules (e.g., `CombatManager`, `DungeonSeeder`, `WorldGenerator`), and synthesizes their structured output into narrative using the `LLMService`.
*   **Modular LLM & API Services:** The application must have a modular `LLMService` (for OpenAI, Gemini, local models) and a modular `ImageGenerationService`.
*   **Post-Generation Parsing:** The Warden Orchestrator will parse its own LLM-generated output to identify and create mechanically significant entities, such as changing a `hidden` location to `rumored` on the map when an NPC mentions one.

---

## 4. High-Level UI Layout: The Warden's Desk

*   **`Sidebar (Player Hub & Tools)`**: A persistent sidebar for character status and secondary tools.
    *   **`Character Vitals`**: An always-visible display for HP, STR, DEX, WIL, Fatigue, and Omens.
    *   **`Inventory`**: A visual 10-slot grid for managing items.
    *   **`Game Controls`**: Buttons for "New Game", "Save Game", and "Load Game".
    *   **`Settings`**: An `st.expander` to configure LLM provider and API keys.
    *   **`Player Oracles`**: An `st.expander` containing player-facing oracle tables.
    *   **`Codex`**: An `st.expander` to view discovered lore.

*   **`Main Area (Session & Context)`**: The primary interaction area.
    *   **`Context View`**: A container at the top of the main area.
        *   **`Map View`**: A view of the world map, showing the player's current location and known/explored areas, rendered using a library like Graphviz. It serves as a purely informational visual aid and is not interactive.
    *   **`Session View`**: The main, scrollable part of the page.
        *   **`Game Log`**: A scrollable, chat-style log of game events and Warden narration, using `st.chat_message`.
        *   **`User Input`**: A `st.chat_input` bar for players to enter their actions, pinned to the bottom of the screen.

---

## 5. Data Models

*   **`GameEntity`**: Represents any character, NPC, or monster.
    *   `id: int` (PK)
    *   `name: str`, `entity_type: str` ("Character", "NPC", "Monster")
    *   `hp: int`, `max_hp: int`, `strength: int`, `max_strength: int`, `dexterity: int`, `max_dexterity: int`, `willpower: int`, `max_willpower: int`, `fatigue: int`
    *   `armor: int`, `disposition: str` ("friendly", "neutral", "hostile")
    *   `age: int`, `pronouns: str`, `description: str`, `background: str`, `bond: str`, `omen: str`
    *   `is_retired: bool`
    *   `attacks: JSON` (e.g., `[{"name": "Bite", "damage": "1d6"}]`)
    *   `current_map_point_id: int` (FK to `MapPoint`)
    *   `current_location_id: int` (FK to `Location`, nullable)

*   **`Item`**:
    *   `id: int` (PK), `name: str`, `description: str`, `quantity: int`
    *   `slots: int`, `tags: list[str]`
    *   `owner_entity_id: int` (FK to `GameEntity`, nullable)
    *   `location_id: int` (FK to `Location`, nullable)

*   **`LogEntry`**:
    *   `id: int` (PK), `created_at: timestamp`, `source: str` ("Player" or "Warden")
    *   `content: str`, `metadata_dict: JSON`
    *   `involved_entities: list[int]` (List of `GameEntity` IDs)

*   **`MapPoint`**: A major point of interest on the world map.
    *   `id: int` (PK), `name: str`, `type: str`, `description: str`, `notes: str`
    *   `status: str` ("hidden", "rumored", "known", "explored")
    *   `position_x: int`
    *   `position_y: int`
    *   `default_location_id: int` (FK to `Location`, nullable)
    
*   **`Location`**: A specific room or area within a `MapPoint`.
    *   `id: int` (PK), `map_point_id: int` (FK to `MapPoint`)
    *   `name: str`, `description: str`, `contents: list[str]`

*   **`LocationConnection`**: Represents a path or connection between two `Location`s within the same `MapPoint`.
    *   `id: int` (PK)
    *   `source_location_id: int` (FK to `Location`)
    *   `destination_location_id: int` (FK to `Location`)
    *   `description: str` (e.g., "a narrow corridor", "a sturdy wooden door", "a rickety rope bridge")
    *   `is_two_way: bool` (defaults to True)

*   **`Path`**: A connection between two `MapPoints`.
    *   `id: int` (PK), `start_point_id: int` (FK to `MapPoint`), `end_point_id: int` (FK to `MapPoint`)
    *   `type: str` ("Standard", "Hidden", "Conditional")
    *   `status: str` ("hidden", "known", "explored")
    *   `watches: int`, `feature: str`

---

## 6. Out of Scope (Future Considerations)
*   Multiplayer functionality.
*   Direct integration with Virtual Tabletops (VTTs).
*   Mobile-native or responsive web UI.
*   Advanced procedural generation beyond the provided tables.
*   Support for third-party Cairn supplements.
