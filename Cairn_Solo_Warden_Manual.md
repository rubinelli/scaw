# Solo Cairn AI Warden - Player's Manual

**Version 1.0**

Welcome, adventurer, to the Cairn Solo Warden. This guide will walk you through using this application to explore the dark and mysterious world of Cairn, powered by your own imagination and a digital, AI-powered Warden.

---

## 1. Understanding the Interface: The Warden's Desk

The application is designed as a "Warden's Desk," a three-column layout that keeps all essential information at your fingertips, minimizing the need to switch screens.

### The Left Column: Player Hub

This column is your character's dashboard. It is always visible and contains:

*   **`VitalsView`**: A quick-glance display of your core stats: Hit Protection (HP), Strength (STR), Dexterity (DEX), Willpower (WIL), Fatigue, and any active Omens.
*   **`InventoryView`**: Your 10-slot inventory, represented as a grid. The first four slots are visually distinct, representing items that are "comfortably carried." Hovering over an item will show its details.

### The Center Column: Session View

This is your primary window into the world and where the story unfolds.

*   **`GameLogView`**: A scrollable, chat-style log of the AI Warden's descriptions and your character's actions. The Warden's text and your inputs are visually distinct to create a clear record of your adventure.
*   **`UserInputBar`**: A persistent text input field at the bottom. This is where you will type all your actions, from speaking to NPCs to engaging in desperate combat.

### The Right Column: Context View

This column provides dynamic information about the world around you.

*   **`MapView`**: An always-visible, informational pointcrawl map. It displays your character's current position with a "You Are Here" marker, discovered points of interest (POIs), and the paths between them. The map is updated automatically as you explore, but it is not interactive. Travel is handled exclusively via the `/travel` command.
*   **`ContextInfoPanel`**: A dynamic panel that changes based on your focus. By default, it shows your notes on the current map location. If you hover over another map point or an entity in the `GameLogView` (like an NPC or creature), this panel will update to show relevant information.

### The Icon Bar

A minimal bar at the top or side of the screen contains icons for less-frequently used, but still important, tools:

*   **`CodexButton`**: Opens your personal, searchable journal with tabs for discovered Lore, Locations, NPCs, and Factions.
*   **`OracleButton`**: Opens a panel allowing you to roll on various oracle tables from the Cairn rulebooks for inspiration.
*   **`SettingsButton`**: Opens the settings modal to configure LLM providers, API keys, etc.
*   **`SaveLoadButton`**: Opens the menu to save your current adventure or load a previous one.

---

## 2. Getting Started

### Starting a New Adventure

From the main menu, select "New Adventure." This will generate a new, unique world and create your first character. The application manages one active adventure at a time. To start a different adventure, you will need to load it from a save file.

### Saving and Loading

Your adventure is stored in a single database file (`.db`). You are in full control of this file.

*   **To Save:** Click the "Save Game" button. Your browser will download the database file for your current adventure. You can save this file anywhere on your computer and rename it for your own records (e.g., `my_first_adventure.db`).
*   **To Load:** From the main menu, use the "Load Game" button to upload a previously saved `.db` file. This will replace the active adventure in the application with the one from the file, allowing you to resume exactly where you left off.

### Creating Your Character

Character creation is designed to be fast and evocative.

1.  **Choose a Background:** The application will prompt you to choose a Background from the *Cairn Player's Guide*. You can either pick one or have the application roll randomly for you.
2.  **Roll Attributes:** The Warden will automatically roll 3d6 for your STR, DEX, and WIL, and 1d6 for your starting HP.
3.  **Accept or Edit:** You will be shown the initial rolls. You have the option to accept them as-is, re-roll, or manually edit the numbers to fit the character concept you have in mind.
4.  **Starting Gear:** Your inventory will be automatically populated with the starting gear from your chosen Background.
5.  **Final Touches:** The Warden will guide you through rolling for your character's traits, bonds, and (if you are the first character in this world) a world-shaping Omen.

### Beginning to Play

Once your character is created, you will find yourself in the game world. The Warden will provide an initial description of your surroundings. From here, your adventure begins. You interact with the world by typing what your character says or does into the `UserInputBar`.

---

## 3. How to Interact: Natural Language

You control your character by describing what you want to do in plain, natural language. The AI Warden is designed to understand your intent and translate it into game mechanics. There are no slash commands to memorize.

Simply type what your character does, says, or thinks in the `UserInputBar`.

### Guiding Principles

*   **Be direct:** State your action clearly.
    *   `I search the desk for hidden drawers.`
    *   `I attack the Cave Lizard with my spear.`
    *   `I ask the blacksmith if she has seen a woman in a blue cloak.`
*   **Be descriptive:** The more detail you provide, the better the Warden can narrate the outcome.
    *   `I try to climb the ivy-covered wall, looking for handholds in the crumbling stone.`
    *   `I offer the guard a waterskin and a friendly smile.`
*   **Interact with the world:** You can interact with anything the Warden describes. If there's a strange altar, you can examine it. If there's an NPC, you can talk to them.
    *   `I read the inscription on the strange altar.`
    *   `I travel to the Whispering Hills.`
    *   `I make camp for the night.`

The Warden will interpret your input, make any necessary dice rolls behind the scenes (which will be noted in the log), and describe the outcome. The goal is to make your interaction feel like you're telling a story, with the Warden as your collaborative partner.
