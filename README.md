# Personal LLM

A lightweight, terminal-based AI assistant powered by local LLMs via Ollama, with intelligent internet search integration and persistent conversation history.

## Features

- **Local-First AI** - Run powerful language models entirely on your machine
- **Smart Search Integration** - AI automatically determines when to search the internet for current information
- **Conversation History** - Persistent chat storage with SQLite database
- **Load & Resume Chats** - Access and continue previous conversations
- **Dual-Model Architecture** - Separate model for intelligent search decision making
- **Multiple Search Engines** - Support for Tavily (fast, paid) and DuckDuckGo (free)
- **Streams Responses** - Live-rendered responses with beautiful terminal formatting
- **Memory Management** - Pre-loads models and handles graceful cleanup
- **Customizable Styling** - Gruvbox-inspired color scheme, fully configurable

## Why Use This?

**For terminal enthusiasts who want:**

- Privacy-focused AI that runs entirely offline (except search)
- Lightweight CLI without Electron bloat or web server overhead
- Simple, fast interaction without leaving the terminal
- Smart internet connectivity only when needed
- Full conversation history with easy access to past chats

**Unlike other solutions:**

- No complex web UI to navigate
- No cloud dependencies for the AI itself
- Intelligent search decisions (not manual triggers)
- Terminal-native with vim-like workflow
- Persistent chat history with easy recall

## Prerequisites

- **Python 3.10+**
- **Ollama** - [Install Ollama](https://ollama.ai)
- **API Keys** (optional):
  - Tavily API key for fast search (not required)
  - DuckDuckGo works without any API key

## Installation

### Automated Setup (Recommended)

**Linux/Mac:**

```bash
git clone https://github.com/yourusername/personal_LLM.git
cd personal_LLM
chmod +x setup.sh
./setup.sh
```

**Windows:**

```bash
git clone https://github.com/yourusername/personal_LLM.git
cd personal_LLM
setup.bat
```

The setup script will:

1. Create a virtual environment
2. Install python dependencies
3. Copy the example config file
4. Prompt you to edit your configuration

### Manual Setup

**1. Install Ollama and Pull Models**

```bash
# Install Ollama (see https://ollama.ai for your platform)

# Pull your preferred model
ollama pull qwen3:8b

# Or try other models:
# ollama pull llama3.1:8b
# ollama pull mistral:7b
```

**2. Clone and Setup**

```bash
git clone https://github.com/yourusername/personal_LLM.git
cd personal_LLM

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**3. Configure**

```bash
# Copy example config
cp config.toml.example config.toml

# Edit config.toml to set your preferred model and settings
```

**4. Set API Keys (Optional)**

For Tavily search (faster, less context bloat):

```bash
# Create .env file
echo "TAVILY_KEY=your_api_key_here" > .env
```

Or use DuckDuckGo (free, no API key needed) by setting `search_engine = "ddgs"` in `config.toml`.

## Running

**After setup:**

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Run the application
cd src
python main.py
```

## Configuration

Edit `config.toml` to customize:

```toml
[model_settings]
# Models
main_model = "qwen3:8b"          # Your primary chat model
search_model = ""                 # Leave empty to use main_model for search decisions

# Model Settings
keep_alive = 60                   # Seconds to keep model in RAM
main_thinking = true              # Enable extended thinking for main model
search_thinking = false           # Enable extended thinking for search model

# Context and instructions
initial_context = "You are an AI assistant with internet access."
system_instructions = ""          # Add custom instructions here

[search_settings]
search_engine = "ddgs"            # Options: "tavily" or "ddgs"
search_headers = "Mozilla/5.0..." # User agent for DuckDuckGo

[style_settings]
# Gruvbox-inspired color scheme (hex codes)
system = "#a89984"
assistant = "#b8bb26"
user = "#83a598"
header = "#ebdbb2"
warning = "#fb4934"
```

## Usage

### Basic Chat

```
> You: What's the weather like today?
[*] Reviewing query...
[*] Searching the web for: current weather Niagara Falls Ontario...
╭─ qwen3:8b ────────────────────────────────────────────────────────────────────────────────╮
│ Hello! 😊 The weather today in Niagara Falls in Ontario is...                             │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

### Commands

**Chat Controls:**

- `/help` - Show available commands
- `/info` - Display current session info (model, search model)
- `/new` - Start a new conversation
- `/exit` - Exit the program

**History Management:**

- `/list` - Show recent chat history (last 3 by default)
- `/list [number]` - Show specific number of recent chats
- `/load [chat_id]` - Load and continue a previous conversation
- `/delete [chat_id]` - Delete a specific chat
- `/delete *` - Delete all chats except current session

**Input Controls:**

- `Enter` - Submit your message
- `Alt + Enter` or `Esc + Enter` - Insert new line (for multi-line messages)

### Search Behavior

The AI automatically decides when to search based on:

- Whether your question requires current information
- If the answer is beyond its training data cutoff

## How It Works

1. **User Input** → Question entered in terminal
2. **Search Decision** → Secondary model determines if web search is needed
3. **Search (if needed)** → Queries Tavily or DuckDuckGo for current info
4. **Response Generation** → Primary model generates response with context
5. **Storage** → Conversation saved to SQLite database with automatic timestamp updates

## Project Structure

```
personal_LLM/
├── src/
│   ├── main.py              # Entry point
│   ├── engine.py            # LLM interaction (Ollama)
│   ├── memory.py            # Database operations
│   ├── search.py            # Web search engines
│   ├── view.py              # Terminal UI (Rich)
│   ├── commands.py          # Command parsing and handling
│   ├── models.py            # Data structures (NamedTuples)
│   ├── exceptions.py        # Custom exceptions
│   └── cleanup_handler.py   # Signal handling for graceful shutdown
├── setup.sh                 # Linux/Mac setup script
├── setup.bat                # Windows setup script
├── config.toml.example      # Example configuration
├── config.toml              # Active configuration (created with script or by user)
├── requirements.txt         # Python dependencies
└── memory.db                # SQLite database (created on first run)
```

## Features In Detail

### Conversation History

- All chats stored in SQLite with timestamps
- "Last Updated" column shows most recent activity
- Load any previous conversation and continue where you left off
- Delete individual chats or clear all history

### Dual-Model Architecture

- Main model handles conversation and responses
- Optional separate search model makes search decisions (saves on context for larger models)
- If no search model specified, the main model handles both at no extra memory overhead

### Smart Context Management

- System messages hidden from view but included in context
- Search results added to context invisibly
- Efficient message history for multi-turn conversations

### Graceful Cleanup

- Automatic model unloading on exit
- Signal handlers for Ctrl+C, terminal close, kill commands
- Database commits ensure no data loss

## Roadmap

- [x] Command parser for chat history
- [x] Resume previous conversations
- [x] History loading and management
- [x] User defined context
- [ ] Implement a 'delete last message' feature
- [ ] Add option to route ddgs through tor network (must install and run tor)
- [ ] Optimize search with ddgs and add configuration
- [ ] Implement explicit `/search [query]` command
- [ ] Better error handling and user feedback
- [ ] Unit tests
- [ ] Export conversations to Markdown/PDF
- [ ] Extra Credit: Conversation branching/versioning

## Contributing

Contributions welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## Known Issues

- Large search results may slow response time
- Model must be available in Ollama before running
- Windows users: SIGHUP signal handling not available (functionality unaffected)

## Troubleshooting

**"Module not found" errors:**

- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

**"Could not connect to Ollama" error:**

- Make sure Ollama is running: `ollama serve`
- Check that your model is installed: `ollama list`

**Colors not displaying correctly:**

- Your terminal may not support 256 colors
- Try a different terminal emulator (Windows Terminal, iTerm2, etc.)

**Permission errors on setup.sh:**

- Run `chmod +x setup.sh` before executing

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for advanced input handling
- [Tavily](https://tavily.com) for fast search API
- [Dux Distributed Global Search](https://duckduckgo.com](https://github.com/deedy5/ddgs) for free search alternative

## Support

If you find this useful, please ⭐ star the repo!

For questions or issues, open an issue on GitHub.

---

**Built by a self-taught developer as a learning project and daily-use tool.**
