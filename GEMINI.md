# Gemini Development Guide: Solo Cairn AI Warden

This document provides a comprehensive guide for developing the Solo Cairn AI Warden application. It synthesizes the Product Requirements Document (PRD), the Player's Manual, and the Development Plan to establish clear architectural patterns, code quality standards, and implementation details.

---

## 1. Core Principles

- **Player-Centric Design:** The user interface and game mechanics should be intuitive, immersive, and forgiving. The player's agency and experience are paramount.
- **Modular Architecture:** The codebase must be organized into discrete, decoupled modules. This is crucial for testability, maintainability, and future extensibility.
- **Test-Driven Development (TDD):** Core logic (especially the orchestrator, game rules, and database interactions) should be developed with a "test-first" mindset to ensure robustness.
- **Mechanics as the Foundation:** The AI Warden's primary role is to narrate the outcomes of the underlying Cairn 2E mechanics and oracle rolls. The LLM synthesizes, it does not invent rules.

---

## 2. Architecture

The application follows a modular architecture centered around a `WardenOrchestrator` that coordinates interactions between the UI, the database, and various services.

### 2.1. Directory Structure

```
scaw/
├── alembic/              # Alembic migration scripts
├── src/
│   ├── core/             # Core application logic
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── orchestrator.py
│   │   ├── world_generator.py
│   │   └── world_manager.py # Manages the "Known World" state
│   ├── database/         # Database models and session management
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── ui/               # Streamlit UI components (Views)
│   │   ├── __init__.py
│   │   ├── sidebar_view.py
│   │   └── main_view.py
│   ├── utils/            # Utility functions
│   └── app.py            # Main Streamlit application entry point
├── tests/                # Pytest tests
├── .streamlit/
│   └── secrets.toml      # Secret management
├── alembic.ini
├── GEMINI.md
└── pyproject.toml
```

### 2.2. Key Components

-   **`app.py` (Entry Point):** Initializes the Streamlit application, manages session state, and delegates UI rendering to the `ui` modules. It should be kept lean.
-   **`WardenOrchestrator` (`core/orchestrator.py`):** The brain of the application. It interprets player intent, selects the appropriate "World Tool" via the `LLMService`, executes the tool, and synthesizes the result into a narrative.
-   **`LLMService` (`core/llm_service.py`):** A modular interface for interacting with different tool-calling Large Language Models (Gemini, OpenAI, local). It abstracts away the specifics of each API.
-   **`World Tools` (`core/world_tools.py`):** A collection of simple, single-purpose Python functions that represent the fundamental, mechanical actions a player can take in the world (e.g., `roll_dice`, `deal_damage`, `add_item_to_inventory`). These are the tools the LLM can choose to use.
-   **Database Models (`database/models.py`):** SQLAlchemy ORM classes that define the application's database schema.
-   **UI Views (`ui/`):** Self-contained functions or classes that render specific parts of the Streamlit UI (e.g., `render_sidebar`, `render_game_log`).
-   **`WorldManager` (`core/world_manager.py`):** Encapsulates the logic for managing the four-state status (`hidden`, `rumored`, `known`, `explored`) of map points and paths.

### 2.3. State Management

-   **Single Source of Truth:** The SQLite database (`.db` file) is the absolute source of truth for all persistent game state.
-   **Streamlit Session State (`st.session_state`):** Use `st.session_state` as a short-term cache for the current session's data to minimize database queries during UI reruns.

---

## 3. Code Quality & Standards

(No changes from previous version)

### 3.1. Linting and Formatting

-   **Tool:** `Ruff`
-   **Command:** `ruff check . --fix && ruff format .`

### 3.2. Type Checking

-   **Tool:** `mypy`
-   **Command:** `mypy src`

### 3.3. Testing

-   **Framework:** `pytest`
-   **Requirement:** Core business logic, especially in `orchestrator.py`, `world_manager.py`, and all `world_tools.py` functions, must have comprehensive unit test coverage.

### 3.4. Commit Messages

-   **Standard:** [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

---

## 4. Implementation Details & Decisions

### 4.1. Configuration and Secrets

-   **Secrets:** Use Streamlit's built-in secrets management (`.streamlit/secrets.toml`).
-   **Application Settings:** Manage in a dedicated configuration file or the Streamlit UI.

### 4.2. The "World Tools" Architecture

-   **Player Input:** The player enters a natural language command (e.g., "I attack the goblin").
-   **Tool Selection:** The `WardenOrchestrator` passes the input and the list of available `world_tools.py` functions to the `LLMService`. The LLM's function-calling/tool-calling capability is used to determine which tool to use and with what arguments (e.g., `deal_damage(target_name='goblin', damage_roll='1d8')`).
-   **Execution & State Change:** The `WardenOrchestrator` receives the chosen tool function and arguments from the LLM. It executes the Python function, which directly interacts with the database to modify the game state (e.g., updating the goblin's HP).
-   **Narrative Synthesis:** The `WardenOrchestrator` takes the result of the tool execution (e.g., `{'success': True, 'damage_dealt': 5, 'target_hp': 2}`) and passes it back to the `LLMService` to generate a compelling narrative description for the player.
-   **Error Handling:** If the player's command is ambiguous or a tool fails, the `WardenOrchestrator` should gracefully handle the error and ask the player for clarification.

### 4.3. Error Handling

-   **User-Facing Errors:** Application errors (invalid commands, failed actions) should be caught and displayed as a clear, user-friendly message in the game log.
-   **System Errors:** Backend errors (LLM API failures, database connection issues) should be logged with a full traceback for debugging, but still present a simple "An error occurred" message to the user to avoid breaking immersion.

### 4.4. RAG Context Store

-   **Integration:** The `LLMService` will be the integration point for the RAG system (Cognee).
-   **Data Flow:** When an adventure is loaded, the `LogEntry` table from the SQLite database will be used to build/rebuild the in-memory RAG index. This ensures the context is always in sync with the canonical game state and that the index is treated as a disposable cache.
