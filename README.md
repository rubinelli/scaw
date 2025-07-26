# SCAW - Solo Cairn AI Warden

**An AI-powered solo tabletop RPG experience for Cairn 2nd Edition**

SCAW (Solo Cairn AI Warden) is a Streamlit application that serves as your personal AI game master for the Cairn 2nd Edition tabletop RPG. The purpose of this project is offering rich, dynamic adventures in the dark fantasy world of Cairn with an intelligent AI that manages game state, generates compelling narratives, and responds to your choices with emergent storytelling.

## ✨ Features

### 🎮 Complete Cairn 2E Implementation
- **Full character creation** with all 20 backgrounds, traits, bonds, and omens
- **Authentic game mechanics** including combat, magic, inventory management, and saving throws
- **Dynamic world generation** with interconnected locations and rich descriptions
- **Tension tracking system** with time-pressured events and meaningful consequences

### 🤖 Advanced AI Game Master
- **LLM-powered orchestration** using tool-calling for precise game state management
- **Dynamic NPC behavior** with relationship tracking and proactive actions
- **RAG-enhanced memory** using ChromaDB and LangChain for consistent narrative context
- **Rich sensory descriptions** that bring the world of Cairn to life

### 🗺️ Persistent World System
- **Multi-adventure support** - Each game is a separate, persistent world
- **Procedural world generation** enhanced by AI for unique, detailed locations
- **Four-state exploration** system (hidden, rumored, known, explored)
- **Consequence propagation** - Your choices permanently shape the world

### 💾 Robust Data Management
- **SQLite databases** with Alembic migrations for reliable data persistence
- **Adventure management** - Create, load, and manage multiple game worlds
- **Character progression** tracking across deaths and new characters
- **Complete game log** preservation for narrative continuity

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- A Google Gemini API key (set a GOOGLE_API_KEY environment variable)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd scaw
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key:**
   Create a `.streamlit/secrets.toml` file:
   ```toml
   [secrets]
   GOOGLE_API_KEY = "your-gemini-api-key-here"
   ```

4. **Initialize the database:**
   ```bash
   alembic upgrade head
   ```

5. **Run the application:**
   ```bash
   streamlit run src/app.py
   ```

### Your First Adventure

1. **Launch SCAW** and you'll see the game launcher
2. **Create a new adventure** by entering a name and clicking "Create New Game"
3. **Generate your character** using the interactive character creation system
4. **Begin your journey** in a procedurally generated world by describing your first action

## 🎯 How to Play

### Basic Commands
SCAW understands natural language input. Try commands like:
- `"I examine the ancient door"`
- `"I attack the goblin with my sword"`
- `"I try to persuade the merchant to lower his prices"`
- `"I search for traps in this room"`
- `"I rest to recover my health"`

### Game Mechanics
- **HP (Hit Protection):** Your ability to avoid serious harm
- **Attributes:** STR, DEX, and WIL determine your capabilities
- **Inventory:** Manage 10 slots of equipment and items
- **Fatigue:** Accumulates from spells and exhaustion
- **Scars:** Permanent marks from near-death experiences

### The Tension System
Every adventure begins with urgent, escalating problems:
- **Time pressure:** Events worsen if ignored
- **Multiple solutions:** Choose your approach carefully
- **Lasting consequences:** Your decisions permanently change the world
- **Dynamic NPCs:** Characters remember and react to your actions

## 🏗️ Technical Architecture

### Core Components
- **WardenOrchestrator:** The central AI that interprets commands and manages game flow
- **LLMService:** Modular interface supporting multiple AI providers
- **WorldGenerator:** Creates rich, interconnected game worlds
- **World Tools:** Atomic functions representing all possible game actions
- **RAGService:** Provides AI with long-term memory of your adventures

### Database Schema
- **GameEntity:** Characters, NPCs, and creatures
- **MapPoint:** Major locations in the world
- **Location:** Specific places within map points
- **Item:** Equipment and objects
- **LogEntry:** Complete narrative history
- **TensionEvent:** Time-pressured story elements

### Supported LLM Providers
- Google Gemini
- OpenAI GPT and local models (via compatible APIs) are planned for future version

### Game Customization
- **World generation parameters** can be adjusted in `world_generator.py`
- **Tension event frequency** and **escalation rates** are configurable
- **NPC behavior patterns** can be modified in the orchestrator

## 🔧 Development

### Project Structure
```
scaw/
├── src/
│   ├── core/           # Core game logic
│   ├── database/       # Data models and migrations
│   ├── ui/            # Streamlit interface components
│   └── app.py         # Main application entry point
├── alembic/           # Database migrations
├── tests/             # Test suite
└── adventures/        # Saved game databases
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
ruff check . --fix && ruff format .
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

## 🎲 About Cairn 2nd Edition

Cairn is a tabletop RPG about exploring a dark and mysterious Wood filled with strange folk, hidden treasure, and unspeakable monstrosities. Key principles include:

- **Neutrality:** The Warden acts as a neutral arbiter
- **Classless:** Characters are defined by equipment and experience
- **Death:** Always present but never random
- **Fiction First:** Story drives mechanics, not the other way around
- **Player Choice:** Information is provided freely and frequently

SCAW tries to faithfully implement these principles while adding the convenience and consistency of an AI game master.

## 🐛 Troubleshooting

### Common Issues

**"Failed to initialize LLM Service"**
- Check that your API key is correctly set in `.streamlit/secrets.toml`
- Verify your API key has the necessary permissions
- Ensure you have internet connectivity

**"Database connection error"**
- Run `alembic upgrade head` to ensure your database is up to date
- Check that the `adventures/` directory exists and is writable

**"Game feels repetitive"**
- The AI learns from your playstyle - try different approaches
- Engage with NPCs and explore dialogue options
- Focus on the tension events for more dynamic gameplay

### Performance Tips
- Close unused adventures to free up memory
- The RAG system improves with longer play sessions
- Complex worlds may take a moment to generate - this is normal

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure code passes linting (`ruff check`)
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pre-commit install
```

## 📄 License

This project is open source. Please respect the intellectual property of the Cairn RPG system.

## 🙏 Credits

- **Cairn 2nd Edition** by Yochai Gal and the Cairn community
- **AI Integration** powered by Google Gemini and other LLM providers
- **Built with** Streamlit, SQLAlchemy, LangChain, and ChromaDB

## 🔗 Links

- [Cairn RPG Official Site](https://cairnrpg.com)
- [Cairn 2nd Edition SRD](https://cairnrpg.com/cairn-srd/)
- [Report Issues](https://github.com/rubinelli/scaw/issues)
