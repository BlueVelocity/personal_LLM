# Personal LLM

A lightweight, terminal-based AI assistant powered by local LLMs via Ollama, with intelligent internet search integration.

## Features

- **Local-First AI** - Run powerful language models entirely on your machine
- **Smart Search Integration** - AI automatically determines when to search the internet for current information
- **Conversation History** - Persistent chat storage with SQLite database
- **Dual-Model Architecture** - Separate model for intelligent search decision making
- **Multiple Search Engines** - Support for Tavily (fast, paid) and DuckDuckGo (free)
- **Streams Responses** - Live-rendered responses with beautiful terminal formatting
- **Memory Management** - Pre-loads models and handles graceful cleanup

## Why Use This?

**For terminal enthusiasts who want:**

- Privacy-focused AI that runs entirely offline (except search)
- Lightweight CLI without Electron bloat or web server overhead
- Simple, fast interaction without leaving the terminal
- Smart internet connectivity only when needed

**Unlike other solutions:**

- No complex web UI to navigate
- No cloud dependencies for the AI itself
- Intelligent search decisions (not manual triggers)
- Terminal-native with vim-like workflow

## Prerequisites

- **Python 3.10+**
- **Ollama** - [Install Ollama](https://ollama.ai)
- **API Keys** (optional):
  - Tavily API key for fast search (recommended but not required)
  - DuckDuckGo works without any API key

## Quick Start

### 1. Install Ollama and Pull Models

```bash
# Install Ollama (see https://ollama.ai for your platform)

# Pull your preferred model
ollama pull qwen3:8b

# Or try other models:
# ollama pull llama3.1:8b
# ollama pull mistral:7b
```

### 2. Clone and Setup

```bash
git clone https://github.com/yourusername/personal_LLM.git
cd personal_LLM

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

```bash
# Copy example config (if you create one)
cp config.toml.example config.toml

# Edit config.toml to set your preferred model
# Default is qwen3:8b
```

### 4. Set API Keys (Optional)

For Tavily search (faster, more reliable):

```bash
# Create .env file
echo "TAVILY_KEY=your_api_key_here" > .env
```

Or use DuckDuckGo (free, no API key needed) by setting `engine_name = "ddgs"` in `config.toml`.
Modify html headers as required.

### 5. Run

```bash
cd src
python main.py
```

## Configuration

Edit `config.toml` to customize:

```toml
[models]
MAIN = "qwen3:8b"          # Your primary chat model
SEARCH = ""                 # Leave empty to use MAIN for search decisions

[memory]
keep_alive = 60             # Seconds to keep model in RAM

[system_prompt]
initial_context = "You are an AI assistant with internet access."
system_instructions = ""    # Add custom instructions here

[search_settings]
engine_name = "tavily"      # Options: "tavily" or "ddgs"
headers = "Mozilla/5.0..."  # User agent for DuckDuckGo
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

- Type your question naturally
- Type `exit` or `quit` to end session
- Press `Ctrl+C` for immediate exit

### Search Behavior

The AI automatically decides when to search based on:

- Whether your question requires current information
- If the answer is beyond its training data

## How It Works

1. **User Input** → Question entered in terminal
2. **Search Decision** → Secondary model determines if web search is needed and the search prompt
3. **Search (if needed)** → Queries Tavily or DuckDuckGo for current info
4. **Response Generation** → Primary model generates response with context
5. **Storage** → Conversation saved to SQLite database

## Roadmap

- [ ] Command parser for chat history (`-history list`, `-history open 2`)
- [ ] Resume previous conversations
- [ ] Implement explicit search requests
- [ ] Add screenshots and demos with asciinema
- [ ] Better error handling and user feedback
- [ ] Docker containerization for easy deployment
- [ ] Unit tests
- [ ] Export conversations to Markdown/PDF
- [ ] Conversation branching/versioning

## Contributing

Contributions welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## Known Issues

- Large search results may slow response time
- Model must be available in Ollama before running

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [Tavily](https://tavily.com) for fast search API
- [DuckDuckGo](https://duckduckgo.com) for free search alternative

## Support

If you find this useful, please ⭐ star the repo!

For questions or issues, open an issue on GitHub.

---

**Built by a self-taught developer. It's my hobby**
