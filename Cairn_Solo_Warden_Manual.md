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

## 3. How to Interact: The Hybrid Input System

You control your character using a hybrid system of natural language and slash commands.

*   **Natural Language:** For most actions, simply describe what you want to do in plain English. This is best for role-playing, conversation, and creative interactions.
    *   `I search the desk for hidden drawers.`
    *   `I ask the blacksmith if she has seen a woman in a blue cloak.`
    *   `I try to climb the ivy-covered wall.`

*   **Slash Commands:** For precise, mechanical actions, slash commands provide clarity and ensure the Warden understands your intent perfectly. This is the preferred method for combat, inventory management, and using specific game functions.

---

## 4. Slash Command Reference

Here is a detailed list of available slash commands. Arguments in `< >` are required, while arguments in `[ ]` are optional.

### Core Actions

*   `/say <message>`: Broadcasts a message to be heard by anyone nearby. Use this for shouting or making general statements. For conversations, it's often more natural to just type the dialogue.
    *   `/say Hello! Is anyone in there?`
*   `/do <action>` or `/action <action>`: Use to perform a specific, non-standard action. It helps clarify your intent to the Warden.
    *   `/do smear mud on my face for camouflage`
*   `/look [target]` or `/examine [target]`: Observe your immediate surroundings or a specific target (object, creature, feature). If no target is specified, the Warden describes the general area.
    *   `/look`
    *   `/examine the strange altar`
*   `/attack <target>`: Declare an attack against a specific target. Combat is fast and dangerous.
    *   `/attack Cave Lizard`

### Movement & Time

*   `/travel <location name>`: Initiate travel to an adjacent, named location on the `MapView`. The Warden will calculate the time in `Watches`.
    *   `/travel 'The Whispering Hills'`
*   `/rest`: Spend a few moments to catch your breath and recover all lost HP. This is not possible in dangerous situations.
*   `/makecamp`: Set up camp for a full 8-hour watch. This is required to heal `Fatigue`, consume rations, and prepare for the next day. This is the primary way to advance time.

### Character & Inventory

*   `/inventory` or `/inv`: Displays a detailed list of your inventory in the `GameLogView`.
*   `/use <item> [on target]`: Use an item from your inventory. If the item is meant to be used on something or someone, specify the target.
    *   `/use Healing Salve on myself`
    *   `/use Iron Spike on the wooden door`
*   `/drop <item>`: Drop an item from your inventory onto the ground.
*   `/equip <item>`: Equip a weapon or piece of armor.
*   `/unequip <item>`: Unequip a weapon or piece of armor.

### Social & Commerce

*   `/talk <target>`: Initiate a direct conversation with an NPC.
    *   `/talk Elara the blacksmith`
*   `/trade <item> for <item> with <target>`: Propose a trade with an NPC.
    *   `/trade my silver ring for her lantern with Elara`
*   `/buy <item>`: Attempt to purchase an item from a merchant.
    *   `/buy Short Sword`
*   `/sell <item>`: Attempt to sell an item to a merchant.
    *   `/sell my extra rope`

### Meta & Utility

*   `/help [command]`: Displays a list of all slash commands, or detailed information about a specific command.
*   `/codex [search term]`: Opens the Codex view. If a search term is provided, it searches your Codex for relevant entries (NPCs, Lore, etc.).
    *   `/codex Elara`
*   `/oracle <table name>`: Opens the Oracle panel. If a table name is provided, it rolls on that specific table and displays the result.
    *   `/oracle Dungeon Seed`
*   `/settings`: Opens the application settings menu.
*   `/gen_image [prompt]`: Generates an image based on the Warden's last description. You can optionally provide your own prompt to guide the generation.
    *   `/gen_image a close up of the rusty, cursed dagger`
