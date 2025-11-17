# DreamingAI - Enhanced Autonomous Reasoning System

DreamingAI is a comprehensive autonomous reasoning system that allows local language models to "dream" independently. The application runs continuous reasoning loops without user prompts, exploring ideas organically and discovering insights through pure thought processes.

## Features

### Core Capabilities
- **Promptless Autonomous Thinking** – AI starts with a blank slate and develops its own reasoning chains
- **Advanced Reasoning Modes** – 9 different thinking strategies including free association, logical deduction, creative speculation, pattern recognition, analogical reasoning, meta-cognition, synthesis, and exploration
- **Web Search Integration** – Optional DuckDuckGo search integration for web-informed reasoning with intelligent caching
- **Interest Detection** – Sophisticated scoring system that identifies interesting thoughts and "golden" discoveries
- **Dual Memory System** – Short-term context (RAM) and long-term persistent storage (SQLite)
- **Local Model Support** – Optimized for [Ollama](https://ollama.ai) with support for small, efficient models

### Advanced Analytics
- **Thought Clustering** – Machine learning-based semantic clustering using TF-IDF and K-means
- **Theme Extraction** – Automatic identification of recurring concepts and patterns
- **Interest Evolution Analysis** – Track how thought quality evolves over sessions
- **Session Analytics** – Comprehensive statistics and performance metrics
- **Visual Analytics** – Multi-panel visualizations of thought patterns and distributions

### Network Analysis
- **Graph Network Analysis** – Analyze thoughts as interconnected networks
- **Centrality Detection** – Identify the most influential and important thoughts
- **Community Detection** – Discover clusters and groups of related thoughts
- **Path Analysis** – Trace reasoning chains from seed to conclusion
- **Interest Propagation** – Track how interest flows through thought networks

### Replay & Simulation
- **Thought Replay** – Replay historical sessions with variable speed control
- **Session Comparison** – Compare multiple sessions side-by-side
- **Simulation Mode** – Test system without LLM calls for development
- **Performance Benchmarking** – Measure and optimize system performance

### Export & Integration
- **JSON Export** – Export thoughts for external analysis
- **Graph Export** – Export network graphs in GEXF, GraphML, JSON formats
- **Visualization Export** – Generate publication-quality visualizations
- **CLI & Programmatic APIs** – Flexible command-line and Python APIs

See documentation files for detailed information:
- `DreamingAI - Autonomous Reasoning System.md` - Philosophy and architecture
- `API_DOCUMENTATION.md` - Complete API reference
- `USER_GUIDE.md` - Comprehensive user guide with examples

## Quick Start

1. Install [Ollama](https://ollama.ai) and download a small model, for example:
   ```bash
   ollama pull qwen2.5:0.5b
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python3 dreaming_ai.py
   ```
4. Choose **start** to begin a dreaming session. Thoughts will appear until you stop the program with `Ctrl+C`.

Golden discoveries and session summaries are saved in the `dream_outputs/` directory and a persistent database file `dreaming_memory.db`.

## Docker

Alternatively, you can run DreamingAI in a container:

```bash
docker-compose up --build
```

The compose file builds the included `Dockerfile`, launches Ollama and starts DreamingAI automatically.

## Advanced Usage

### Web Search Integration

Enable web-informed reasoning:
```bash
# Edit config.json
{
  "enable_web_search": true,
  "web_search_max_results": 3,
  "web_search_cache_ttl": 3600
}
```

The AI will automatically search the web when encountering interesting topics and incorporate results into its reasoning.

### Analytics and Visualization

Generate comprehensive analytics:
```bash
# Interactive mode - option 3
python3 dreaming_ai.py
# Choose: 3 (analyze)

# Or direct analysis
python3 dreaming_ai.py --analyze
```

Creates:
- Thought clustering analysis
- Theme extraction
- Interest score statistics
- Visualization charts (4-panel analysis)

### Thought Replay

Replay historical sessions:
```bash
# List all sessions
python3 thought_replay.py --list-sessions

# Replay a specific session at 2x speed
python3 thought_replay.py --replay session_12345 --speed 2.0

# Analyze a session
python3 thought_replay.py --analyze session_12345

# Compare two sessions
python3 thought_replay.py --compare session_123 session_456

# Simulate a test session
python3 thought_replay.py --simulate 50
```

### Network Graph Analysis

Analyze thought relationships as networks:
```bash
# Build and analyze thought graph
python3 thought_graph.py --build --central --communities

# Create visualization
python3 thought_graph.py --build --visualize thought_network.png

# Analyze thought flow
python3 thought_graph.py --build --flow --propagation

# Export graph for Gephi or other tools
python3 thought_graph.py --build --export thought_graph.gexf

# Calculate network metrics
python3 thought_graph.py --build --metrics
```

### Comprehensive Testing

Run the full test suite:
```bash
# Run all tests
python3 test_dreaming_ai.py

# Run with verbose output
python3 -m unittest test_dreaming_ai -v

# Run specific test case
python3 -m unittest test_dreaming_ai.TestInterestDetector
```

Test coverage includes:
- Thought data structures
- Seed generation
- Interest detection algorithms
- Memory system operations
- Web search engine
- Thought clustering
- Analytics functions
- Export functionality
- Integration tests

## Repository Contents

### Core Files
- `dreaming_ai.py` – Enhanced main application with web search and advanced analytics
- `test_dreaming_ai.py` – Comprehensive unit test suite
- `thought_replay.py` – Session replay and simulation tools
- `thought_graph.py` – Network graph analysis tools
- `config.json` – Configuration with web search and advanced settings
- `requirements.txt` – All Python dependencies including analytics libraries
- `Dockerfile` / `docker-compose.yml` – Container setup

### Documentation
- `README.md` – This file
- `API_DOCUMENTATION.md` – Complete API reference with examples
- `USER_GUIDE.md` – Comprehensive user guide for all features
- `DreamingAI - Autonomous Reasoning System.md` – Philosophy and architecture
- `DreamingAI Deployment Guide.md` – Deployment instructions
- `Multi-Agent Thinking System Architecture Design.md` – Future multi-agent design
- `ATAGLANCE.MD` – Quick overview
- `todo.md` – Project roadmap and completed features

## Configuration Options

The `config.json` file supports extensive customization:

```json
{
  "model": "qwen2.5:0.5b",
  "ollama_url": "http://localhost:11434",
  "db_path": "dreaming_memory.db",
  "output_dir": "dream_outputs",

  "reasoning_strategies": {
    "free_association": 0.25,
    "logical_deduction": 0.15,
    "creative_what_if": 0.15,
    "pattern_recognition": 0.15,
    "analogical_reasoning": 0.1,
    "meta_cognition": 0.1,
    "synthesis": 0.05,
    "exploration": 0.05
  },

  "interest_threshold": 0.4,
  "dream_interval": 5,
  "max_thoughts_per_session": 100,

  "enable_web_search": true,
  "web_search_cache_ttl": 3600,
  "web_search_max_results": 3,

  "enable_branching": false,
  "branch_probability": 0.1
}
```

## Performance & Optimization

### Recommended Configurations

**Fast Exploration** (Quick idea generation):
```json
{
  "model": "qwen2.5:0.5b",
  "dream_interval": 2,
  "max_thoughts_per_session": 50,
  "enable_web_search": false
}
```

**Deep Thinking** (Quality over speed):
```json
{
  "model": "gemma2:2b",
  "dream_interval": 8,
  "max_thoughts_per_session": 100,
  "enable_web_search": true,
  "reasoning_strategies": {
    "meta_cognition": 0.3,
    "synthesis": 0.2,
    "logical_deduction": 0.25,
    "pattern_recognition": 0.25
  }
}
```

**Research Mode** (Web-informed reasoning):
```json
{
  "model": "gemma2:2b",
  "enable_web_search": true,
  "web_search_max_results": 5,
  "reasoning_strategies": {
    "synthesis": 0.3,
    "pattern_recognition": 0.3,
    "exploration": 0.2,
    "meta_cognition": 0.2
  }
}
```

## Use Cases

1. **Creative Writing** - Generate story ideas and explore narrative possibilities
2. **Research Brainstorming** - Explore research directions with web-informed reasoning
3. **Philosophical Exploration** - Deep contemplation on abstract concepts
4. **Problem Solving** - Explore solution spaces through divergent thinking
5. **Learning & Education** - Make connections between concepts automatically
6. **Content Generation** - Generate blog post ideas, article outlines, etc.
7. **Pattern Discovery** - Identify hidden connections in complex topics

## Troubleshooting

### Common Issues

**Web search not working:**
```bash
pip install duckduckgo-search
# Enable in config.json: "enable_web_search": true
```

**Visualization errors:**
```bash
pip install matplotlib numpy networkx
```

**Database locked:**
Use separate database files for concurrent sessions:
```bash
python3 dreaming_ai.py --config config1.json  # config1: "db_path": "dreams1.db"
python3 dreaming_ai.py --config config2.json  # config2: "db_path": "dreams2.db"
```

**Ollama connection error:**
```bash
# Ensure Ollama is running
ollama serve

# In another terminal
python3 dreaming_ai.py
```

## Contributing

Contributions welcome! Areas for enhancement:
- Additional reasoning modes
- Alternative LLM backends (OpenAI, Anthropic, local transformers)
- Advanced visualization techniques
- Multi-agent interactions
- Real-time collaboration features
- Mobile/web interfaces
- Integration with note-taking apps

## Citation

If you use DreamingAI in your research or projects, please cite:

```bibtex
@software{dreamingai2024,
  title = {DreamingAI: Autonomous Reasoning System for Language Models},
  year = {2024},
  url = {https://github.com/yourusername/ai-dreaming2},
  note = {Enhanced with web search, analytics, and network analysis}
}
```

## License

This project is released under the MIT license. See the source files for details.

## Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- Uses DuckDuckGo for web search integration
- Network analysis powered by NetworkX
- Machine learning features via scikit-learn
- Visualizations created with Matplotlib

---

**Version:** 2.0.0 (Enhanced)
**Status:** Production Ready
**Python:** 3.8+
**License:** MIT
