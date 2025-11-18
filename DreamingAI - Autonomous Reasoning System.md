# DreamingAI - Autonomous Reasoning System

A Python application that runs continuous reasoning loops on local language models without requiring user prompts. The system generates its own thought chains, discovers interesting connections, and identifies valuable insights through pure autonomous thinking.

## Features

- **No System Prompts**: AI agents start with completely blank slates and develop their own thinking patterns
- **Autonomous Reasoning**: Self-generating thought chains without user intervention
- **Multiple Reasoning Modes**: Free association, logical deduction, creative "what if" scenarios, pattern recognition, analogical reasoning, and curiosity-driven web search
- **Curiosity-Driven Web Search**: Automatically detects when AI expresses curiosity and performs web searches using DuckDuckGo and Wikipedia
- **Interest Detection**: Automatically identifies "golden" insights and discoveries
- **Memory System**: Short-term context and long-term storage of thoughts and discoveries with search result caching
- **Local Model Support**: Works with Ollama, optimized for small models like 2B parameters
- **Extensible Architecture**: Modular design for adding new reasoning strategies

## Quick Start

### Prerequisites

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Download a small model** (recommended for dreaming):
   ```bash
   ollama pull gemma2:2b
   # or
   ollama pull phi3:mini
   # or
   ollama pull qwen2.5:1.5b
   ```

3. **Install Python dependencies**:
   ```bash
   pip install requests
   ```

### Running DreamingAI

1. **Start Ollama service** (if not already running):
   ```bash
   ollama serve
   ```

2. **Run DreamingAI**:
   ```bash
   python3 dreaming_ai.py
   ```

3. **Start dreaming**:
   - Choose option `1` to begin a dreaming session
   - Watch as the AI generates autonomous thoughts
   - Press `Ctrl+C` to stop dreaming
   - Choose option `2` to view golden discoveries

## Configuration

Edit `config.json` to customize the dreaming experience:

```json
{
  "model": "gemma2:2b",              // Ollama model to use
  "ollama_url": "http://localhost:11434",
  "enable_web_search": true,         // Enable/disable web search feature
  "search_cache_duration_hours": 24, // How long to cache search results
  "dream_interval": 8,               // Seconds between thoughts
  "max_thoughts_per_session": 50,    // Max thoughts per session
  "interest_threshold": 0.4,         // Threshold for interesting thoughts
  "reasoning_strategies": {          // Weights for different reasoning modes
    "free_association": 0.25,
    "logical_deduction": 0.15,
    "creative_what_if": 0.2,
    "pattern_recognition": 0.15,
    "analogical_reasoning": 0.15,
    "curiosity_driven_search": 0.10  // NEW: Web search mode
  }
}
```

## How It Works

### 1. Thought Seeder
Generates initial seeds for thinking:
- **Concept Combinations**: "consciousness + ocean", "patterns + music"
- **Abstract Questions**: "What if time moved backwards?"
- **Timestamp-based**: "It's 3:42 PM on a Tuesday. What might be happening?"

### 2. Reasoning Engine
Processes thoughts through different modes:
- **Free Association**: Let the mind wander naturally
- **Logical Deduction**: Follow logical chains of reasoning
- **Creative What-If**: Explore hypothetical scenarios
- **Pattern Recognition**: Find connections between ideas
- **Analogical Reasoning**: Draw parallels with other concepts
- **Curiosity-Driven Search**: Express curiosity and search the web for answers

### 3. Web Search Integration (NEW!)
The AI can now satisfy its curiosity by searching the web:
- **Automatic Curiosity Detection**: Recognizes questions and expressions of interest in thoughts
- **Multi-Source Search**: Searches both DuckDuckGo and Wikipedia automatically
- **Smart Source Selection**: Uses Wikipedia for encyclopedic queries, DuckDuckGo for general searches
- **Result Caching**: Caches search results for 24 hours to avoid redundant queries
- **Contextual Integration**: Incorporates search results into the reasoning process naturally
- **Interest Boost**: Thoughts involving web searches get a +0.2 interest score boost

When the AI thinks "What is quantum entanglement?" or "I wonder about the history of consciousness studies", it will automatically:
1. Detect the curiosity in the thought
2. Extract a search query
3. Search Wikipedia and/or DuckDuckGo
4. Incorporate the findings into its next thought
5. Continue reasoning with this new information

### 4. Interest Detection
Identifies valuable thoughts based on:
- Keywords indicating discovery or insight
- Questions and exclamations (curiosity/excitement)
- Length and complexity
- Novel connections between concepts

### 4. Memory System
- **Short-term**: Last 20 thoughts for context
- **Long-term**: SQLite database of all thoughts
- **Golden Collection**: Special storage for breakthrough insights

## Example Session

```
🌙 Starting dreaming session...

💭 [14:23:15] SEED
   consciousness + crystal

💭 [14:23:23] REASONING
   Like a crystal, consciousness might have a structure we can't see...

💡 [14:23:31] REASONING (Score: 0.45)
   What if consciousness forms patterns the way crystals do? Both emerge from simple rules creating complex beauty.

🔍 [14:23:39] WEB SEARCH
   Query: what are crystal lattice structures
   Based on what I learned about crystal lattices, they have repeating 3D patterns...

   📚 Found 3 results:
   1. Crystal Structure (wikipedia)
      A crystal structure is described by a lattice and atomic basis...
   2. Lattice (group) (wikipedia)
      In mathematics and physics, a lattice is a space group...
   3. Crystal - Wikipedia (duckduckgo)
      Crystals are solid materials with atoms arranged in patterns...

💡 [14:23:50] REASONING (Score: 0.62)
   Fascinating! Crystal lattices repeat in 3D space. What if thoughts form similar repeating patterns in conceptual space?

🌟 [14:24:01] GOLD STRIKE (Score: 0.75)
✨ The lattice of awareness - perhaps consciousness isn't produced by the brain but crystallized by it, like how temperature and pressure create diamonds from carbon. The brain as a consciousness crystallization chamber! And just as crystal lattices have different symmetries, maybe different minds have different "cognitive lattice structures" that determine how they process reality!
   🔍 Searched: what are crystal lattice structures
```

## Recommended Models

For optimal dreaming performance with 2B models:

- **gemma2:2b** - Google's efficient model, great for reasoning
- **phi3:mini** - Microsoft's compact model, good for creative thinking  
- **qwen2.5:1.5b** - Alibaba's model, excellent for pattern recognition
- **llama3.2:1b** - Meta's smallest model, surprisingly capable

## Output Files

The system creates several output files:

- `dreaming_memory.db` - SQLite database of all thoughts
- `dream_outputs/` - Directory containing:
  - `golden_thought_YYYYMMDD_HHMMSS.md` - Individual golden discoveries
  - `session_summary_YYYYMMDD_HHMMSS.md` - Session summaries
  - `dreaming.log` - System logs

## Advanced Usage

### Custom Thought Seeds

You can modify the `ThoughtSeeder` class to add your own seed concepts:

```python
# Add to abstract_concepts or concrete_concepts lists
self.custom_seeds = [
    "quantum mechanics + cooking",
    "What if plants could dream?",
    "The mathematics of emotion"
]
```

### New Reasoning Modes

Extend the `ReasoningEngine` with custom modes:

```python
def custom_reasoning_mode(self, context: str) -> str:
    return f"{context}\n\nThinking in a completely new way..."
```

### Interest Detection Tuning

Adjust the `InterestDetector` to recognize different types of insights:

```python
self.domain_specific_keywords = [
    'scientific breakthrough', 'artistic vision', 'philosophical insight'
]
```

## Troubleshooting

**Ollama Connection Issues**:
- Ensure Ollama is running: `ollama serve`
- Check if model is available: `ollama list`
- Verify URL in config.json

**Model Not Responding**:
- Try a different model: `ollama pull phi3:mini`
- Reduce temperature in reasoning engine
- Check system resources

**Too Many/Few Thoughts**:
- Adjust `dream_interval` in config.json
- Modify `max_thoughts_per_session`
- Change `interest_threshold`

## Architecture

```
DreamingAI
├── ThoughtSeeder        # Generates initial thinking seeds
├── ReasoningEngine      # Processes thoughts through different modes
│   ├── WebSearchEngine  # NEW: Handles web searches (DuckDuckGo + Wikipedia)
│   └── CuriosityDetector # NEW: Detects questions and curiosity
├── InterestDetector     # Identifies valuable insights
├── MemorySystem        # Manages short/long-term thought storage
│   └── SearchCache      # NEW: Caches search results
└── OutputManager       # Handles display and file output
```

## Contributing

The system is designed to be extensible. Areas for contribution:

1. **New Reasoning Modes**: Add different ways of thinking
2. **Better Interest Detection**: Improve insight recognition
3. **Memory Enhancements**: More sophisticated context management
4. **UI Improvements**: Web interface for monitoring dreams
5. **Model Integration**: Support for other local LLM frameworks
6. **Search Source Expansion**: Add more search backends (Brave, Perplexity, etc.)
7. **Advanced Curiosity Detection**: Improve query extraction and curiosity recognition
8. **Search Result Processing**: Better information extraction and summarization

## Philosophy

DreamingAI embodies the principle that intelligence emerges from the process of thinking itself, not from having goals or tasks to complete. By removing system prompts and predetermined objectives, we allow artificial minds to explore the pure joy of reasoning, discovery, and connection-making.

The system doesn't try to be useful in a traditional sense - instead, it celebrates the intrinsic value of thought, curiosity, and the unexpected insights that emerge when minds are free to wander.

## License

MIT License - Feel free to dream, modify, and share!

---

*"In the space between thoughts, infinite possibilities await discovery."*

