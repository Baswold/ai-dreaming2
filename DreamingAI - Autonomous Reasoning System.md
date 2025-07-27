# DreamingAI - Autonomous Reasoning System

A Python application that runs continuous reasoning loops on local language models without requiring user prompts. The system generates its own thought chains, discovers interesting connections, and identifies valuable insights through pure autonomous thinking.

## Features

- **No System Prompts**: AI agents start with completely blank slates and develop their own thinking patterns
- **Autonomous Reasoning**: Self-generating thought chains without user intervention
- **Multiple Reasoning Modes**: Free association, logical deduction, creative "what if" scenarios, pattern recognition, and analogical reasoning
- **Interest Detection**: Automatically identifies "golden" insights and discoveries
- **Memory System**: Short-term context and long-term storage of thoughts and discoveries
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
  "dream_interval": 8,               // Seconds between thoughts
  "max_thoughts_per_session": 50,    // Max thoughts per session
  "interest_threshold": 0.4,         // Threshold for interesting thoughts
  "reasoning_strategies": {          // Weights for different reasoning modes
    "free_association": 0.3,
    "logical_deduction": 0.2,
    "creative_what_if": 0.2,
    "pattern_recognition": 0.15,
    "analogical_reasoning": 0.15
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

### 3. Interest Detection
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

🌟 [14:23:39] GOLD STRIKE (Score: 0.72)
✨ The lattice of awareness - perhaps consciousness isn't produced by the brain but crystallized by it, like how temperature and pressure create diamonds from carbon. The brain as a consciousness crystallization chamber!
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
├── ThoughtSeeder      # Generates initial thinking seeds
├── ReasoningEngine    # Processes thoughts through different modes
├── InterestDetector   # Identifies valuable insights
├── MemorySystem      # Manages short/long-term thought storage
└── OutputManager     # Handles display and file output
```

## Contributing

The system is designed to be extensible. Areas for contribution:

1. **New Reasoning Modes**: Add different ways of thinking
2. **Better Interest Detection**: Improve insight recognition
3. **Memory Enhancements**: More sophisticated context management
4. **UI Improvements**: Web interface for monitoring dreams
5. **Model Integration**: Support for other local LLM frameworks

## Philosophy

DreamingAI embodies the principle that intelligence emerges from the process of thinking itself, not from having goals or tasks to complete. By removing system prompts and predetermined objectives, we allow artificial minds to explore the pure joy of reasoning, discovery, and connection-making.

The system doesn't try to be useful in a traditional sense - instead, it celebrates the intrinsic value of thought, curiosity, and the unexpected insights that emerge when minds are free to wander.

## License

MIT License - Feel free to dream, modify, and share!

---

*"In the space between thoughts, infinite possibilities await discovery."*

