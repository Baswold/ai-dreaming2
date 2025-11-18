# DreamingAI Deployment Guide

## 🎯 Quick Start (Recommended)

### Option 1: Direct Python Execution
```bash
# 1. Ensure Ollama is running
ollama serve

# 2. Download a small model (0.5B parameters)
ollama pull qwen2.5:0.5b

# 3. Run DreamingAI
cd dreaming_ai
python3 dreaming_ai.py

# 4. Choose option "1" to start dreaming
```

### Option 2: Docker Deployment
```bash
# Build and run with Docker Compose
cd dreaming_ai
docker-compose up --build

# The system will automatically download the model and start
```

## 🧠 What You'll See

When the AI starts dreaming, you'll see output like:
```
🌙 Starting dreaming session...

💭 [14:23:15] SEED
   consciousness + crystal

💭 [14:23:23] REASONING
   Like a crystal, consciousness might have a structure we can't see...

💡 [14:23:31] REASONING (Score: 0.45)
   What if consciousness forms patterns the way crystals do?

🔍 [14:23:39] WEB SEARCH
   Query: what are crystal lattice structures
   Based on what I learned, crystal lattices have repeating 3D patterns...

   📚 Found 3 results:
   1. Crystal Structure (wikipedia)
      A crystal structure is described by a lattice...
   2. Lattice (group) (wikipedia)
      In mathematics and physics, a lattice is a space...

🌟 [14:23:50] GOLD STRIKE (Score: 0.75)
✨ The lattice of awareness - perhaps consciousness isn't produced
   by the brain but crystallized by it! And just like crystal lattices,
   different minds might have different "cognitive lattice structures"!
   🔍 Searched: what are crystal lattice structures
```

## 🔧 Configuration

Edit `config.json` to customize:
- `dream_interval`: Time between thoughts (seconds)
- `max_thoughts_per_session`: Maximum thoughts per session
- `model`: Which Ollama model to use
- `interest_threshold`: Minimum score for "interesting" thoughts
- `enable_web_search`: Enable/disable web search (true/false)
- `search_cache_duration_hours`: How long to cache search results (default: 24)

## 📁 Output Files

The system creates:
- `dreaming_memory.db` - SQLite database of all thoughts
- `dream_outputs/golden_thought_*.md` - Golden discoveries
- `dream_outputs/session_summary_*.md` - Session summaries
- `dream_outputs/dreaming.log` - System logs

## 🎛️ Available Commands

1. **start** - Begin autonomous dreaming session
2. **golden** - View all golden thoughts discovered
3. **quit** - Exit the application

## 🔍 Memory Requirements

- **qwen2.5:0.5b**: ~400MB RAM (recommended)
- **phi3:mini**: ~2GB RAM
- **gemma2:2b**: ~3GB RAM

## 🚀 Advanced Usage

### Adding Custom Thought Seeds
Edit the `ThoughtSeeder` class to add your own concepts:
```python
self.custom_concepts = [
    "quantum mechanics", "poetry", "mathematics",
    "What if colors had emotions?",
    "How do ideas reproduce?"
]
```

### Adjusting Reasoning Modes
Modify weights in `config.json`:
```json
"reasoning_strategies": {
    "free_association": 0.4,
    "creative_what_if": 0.3,
    "pattern_recognition": 0.2,
    "logical_deduction": 0.1
}
```

## 🎨 Philosophy

DreamingAI embodies pure autonomous thinking:
- **No system prompts** - The AI starts with a blank slate
- **No goals or tasks** - Just pure curiosity-driven exploration
- **Emergent insights** - Discoveries arise naturally from the thinking process
- **Interest-driven** - The AI decides what's worth exploring further

This represents a different paradigm from task-oriented AI - instead of trying to be "useful," it celebrates the intrinsic value of thought and discovery.

## 🛠️ Troubleshooting

**Model memory issues**: Use smaller models like `qwen2.5:0.5b`
**Ollama not responding**: Restart with `sudo systemctl restart ollama`
**No interesting thoughts**: Lower `interest_threshold` in config
**Too fast/slow thinking**: Adjust `dream_interval` in config

## 🌟 What Makes This Special

Unlike traditional AI systems that need prompts and goals, DreamingAI:
- Thinks for the pure joy of thinking
- Discovers unexpected connections between concepts
- Develops its own interests over time
- Records breakthrough insights automatically
- Runs completely locally for privacy
- **NEW: Satisfies its own curiosity** by searching the web when it encounters interesting questions
- **NEW: Learns from external knowledge** and integrates it into its reasoning

The system demonstrates that intelligence can emerge from the process of thinking itself, without external direction or predetermined objectives. With web search integration, the AI can now expand its knowledge autonomously, making it even more capable of generating novel insights and discoveries.

