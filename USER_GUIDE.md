# DreamingAI User Guide

## Welcome to DreamingAI!

This comprehensive guide will help you get the most out of DreamingAI, an autonomous reasoning system that lets AI models "dream" and explore ideas independently.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Concepts](#understanding-the-concepts)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Customization Guide](#customization-guide)
6. [Best Practices](#best-practices)
7. [Real-World Use Cases](#real-world-use-cases)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Getting Started

### Prerequisites

Before using DreamingAI, you need:

1. **Python 3.8 or higher**
   ```bash
   python3 --version
   ```

2. **Ollama** - Local LLM runtime
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull a model (recommended: smaller models for faster dreams)
   ollama pull qwen2.5:0.5b
   # OR
   ollama pull gemma2:2b
   ```

3. **Required Python packages**
   ```bash
   pip install -r requirements.txt
   ```

### Quick Start (5 Minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ollama:**
   ```bash
   ollama serve
   ```

3. **Run DreamingAI:**
   ```bash
   python3 dreaming_ai.py
   ```

4. **Choose "start" from the menu and watch your AI dream!**

### Docker Quick Start

If you prefer Docker:

```bash
# Build and run
docker-compose up --build

# The system will automatically:
# - Install Ollama
# - Pull the model
# - Start dreaming
```

## Understanding the Concepts

### What is "Dreaming"?

In DreamingAI, "dreaming" means autonomous reasoning without specific prompts or goals. The AI:
- Starts with a random seed thought
- Generates follow-up thoughts based on context
- Explores ideas through various reasoning modes
- Identifies and saves particularly interesting discoveries

### Key Components

#### 1. **Thought Seeds**
Initial sparks that start a dreaming session:
- "consciousness + infinity"
- "What if time moved backwards?"
- "The contrast between chaos and order"

#### 2. **Reasoning Modes**
Different ways the AI thinks:
- **Free Association**: Unstructured creative wandering
- **Logical Deduction**: Step-by-step reasoning
- **Creative What-If**: Imaginative speculation
- **Pattern Recognition**: Identifying connections
- **Analogical Reasoning**: Reasoning by similarity
- **Meta-Cognition**: Thinking about thinking
- **Synthesis**: Combining multiple ideas
- **Exploration**: Discovering adjacent concepts
- **Web-Informed**: Using web search results

#### 3. **Interest Scoring**
Each thought receives an interest score (0.0 to 1.0) based on:
- Use of interesting keywords
- Questions asked
- Novel concepts introduced
- Length and complexity
- Discovery indicators ("breakthrough", "aha", etc.)

#### 4. **Golden Thoughts**
Highly interesting discoveries (score > 0.6) are saved as "golden thoughts" for later review.

#### 5. **Memory System**
- **Short-term**: Last 20 thoughts (in RAM)
- **Long-term**: All thoughts (SQLite database)
- Enables context-aware reasoning

## Basic Usage

### Interactive Mode

```bash
python3 dreaming_ai.py
```

You'll see a menu:
```
Commands:
1. start    - Begin dreaming session
2. golden   - Show golden thoughts
3. analyze  - Analyze thought patterns
4. export   - Export thoughts to JSON
5. viz      - Create visualizations
6. quit     - Exit application
```

#### Starting a Dream Session

1. Type `1` or `start`
2. Watch thoughts appear in real-time
3. Press `Ctrl+C` to stop
4. Review the session summary

**Example Output:**
```
💭 [14:23:15] SEED
   consciousness + infinity

💡 [14:23:22] REASONING (Score: 0.47)
   What if consciousness could expand infinitely?

🌟 [14:23:30] GOLD STRIKE (Score: 0.82)
✨ This reveals a fundamental paradox: infinite expansion...
============================================================
```

#### Viewing Golden Thoughts

```
Command: 2

✨ 5 Golden Thoughts Discovered:

1. **Score: 0.92** - 2024-01-15 14:23:30
   This reveals a fundamental paradox between infinity and boundaries...
   📚 Web-informed: 2 sources
------------------------------------------------------------
```

#### Analyzing Patterns

```
Command: 3

🔍 Analyzing all thoughts in database...
Total thoughts in database: 247

📊 Clustering thoughts...
Found 5 clusters:
Cluster 1: 63 thoughts
  Representative: The emergence of patterns from chaos...

🎨 Top themes across all thoughts:
 1. consciousness: 42
 2. patterns: 38
 3. emergence: 31
```

### Command Line Mode

For automation and scripting:

```bash
# Auto-start with 50 thoughts
python3 dreaming_ai.py --auto-start --max-thoughts 50

# Quiet mode (minimal output)
python3 dreaming_ai.py --auto-start --quiet

# Analyze existing data
python3 dreaming_ai.py --analyze

# Export to JSON
python3 dreaming_ai.py --export json

# Custom config
python3 dreaming_ai.py --config my_config.json --auto-start
```

## Advanced Features

### Web Search Integration

Enable the AI to search the web during dreaming:

**config.json:**
```json
{
  "enable_web_search": true,
  "web_search_max_results": 3,
  "web_search_cache_ttl": 3600
}
```

When enabled:
- AI extracts searchable terms from thoughts
- Performs web searches (cached for 1 hour)
- Incorporates results into reasoning

**Example:**
```
💡 [14:25:10] WEB SEARCH (Score: 0.65)
   Based on recent research about quantum entanglement...
   📚 Web-informed
```

### Thought Branching

Create divergent reasoning paths:

**config.json:**
```json
{
  "enable_branching": true,
  "branch_probability": 0.15
}
```

Benefits:
- Explore multiple ideas simultaneously
- Prevent getting stuck in one line of thinking
- Discover unexpected connections

### Visualization and Analytics

Generate visual analyses:

```bash
# Create visualizations
python3 dreaming_ai.py
# Choose option 5 (viz)
```

Creates a 4-panel visualization:
1. **Interest Score Over Time**: Track thought quality
2. **Thought Type Distribution**: See reasoning mode usage
3. **Interest Score Distribution**: Histogram of scores
4. **Thought Length Over Time**: Detect verbosity patterns

### Data Export

Export for external analysis:

```python
from dreaming_ai import DreamingAI

ai = DreamingAI()
ai.export_data(format='json')
```

**Export Format:**
```json
{
  "export_time": "2024-01-15T14:30:00",
  "total_thoughts": 247,
  "thoughts": [
    {
      "id": "thought_123",
      "timestamp": "2024-01-15T14:23:15",
      "content": "consciousness + infinity",
      "type": "seed",
      "interest_score": 0.35,
      "tags": [],
      "web_sources": []
    }
  ]
}
```

## Customization Guide

### Configuring Reasoning Strategies

Adjust the probability distribution of reasoning modes:

**config.json:**
```json
{
  "reasoning_strategies": {
    "free_association": 0.30,      // More creative wandering
    "logical_deduction": 0.10,     // Less structured logic
    "creative_what_if": 0.25,      // More speculation
    "pattern_recognition": 0.15,
    "analogical_reasoning": 0.10,
    "meta_cognition": 0.05,
    "synthesis": 0.03,
    "exploration": 0.02
  }
}
```

Total must sum to approximately 1.0.

### Adjusting Dream Pace

Control how fast thoughts generate:

```json
{
  "dream_interval": 3,  // 3 seconds between thoughts (fast)
  // OR
  "dream_interval": 10  // 10 seconds (slow, contemplative)
}
```

**Recommendations:**
- **Fast (1-3s)**: Good for exploring many ideas quickly
- **Medium (5-8s)**: Balanced, good default
- **Slow (10-15s)**: Deeper, more contemplative sessions

### Interest Threshold

Set minimum score for "interesting" thoughts:

```json
{
  "interest_threshold": 0.4,  // Default
  // OR
  "interest_threshold": 0.6   // Only show highly interesting
}
```

### Model Selection

Choose your AI model:

```json
{
  "model": "qwen2.5:0.5b",    // Fastest, good for rapid dreaming
  // OR
  "model": "gemma2:2b",        // Balanced
  // OR
  "model": "llama3:8b"         // Slower, more sophisticated
}
```

**Model Comparison:**

| Model | Speed | Quality | RAM Usage | Best For |
|-------|-------|---------|-----------|----------|
| qwen2.5:0.5b | ⚡⚡⚡ | ⭐⭐ | 1GB | Quick experiments |
| gemma2:2b | ⚡⚡ | ⭐⭐⭐ | 2GB | Balanced use |
| llama3:8b | ⚡ | ⭐⭐⭐⭐ | 8GB | Deep thinking |

## Best Practices

### 1. Start Small

Begin with short sessions to understand the system:
```json
{
  "max_thoughts_per_session": 20,
  "dream_interval": 5
}
```

### 2. Monitor Golden Thoughts

Regularly review your golden discoveries:
```bash
python3 dreaming_ai.py
# Choose option 2 (golden)
```

### 3. Use Appropriate Models

- **Experimenting**: Use small models (qwen2.5:0.5b)
- **Production**: Use medium models (gemma2:2b)
- **Research**: Use large models (llama3:8b)

### 4. Enable Web Search Selectively

Web search adds latency. Enable only when you want external knowledge:
```json
{
  "enable_web_search": true,  // For research sessions
  "enable_web_search": false  // For pure introspection
}
```

### 5. Regular Database Maintenance

Keep your database healthy:
```bash
# Backup database
cp dreaming_memory.db dreaming_memory_backup.db

# Vacuum to optimize
sqlite3 dreaming_memory.db "VACUUM;"
```

### 6. Experiment with Seeds

Different seed types yield different thinking styles:
- **Philosophical**: Deep, abstract thinking
- **Metaphor**: Creative, imaginative
- **Combination**: Unexpected connections
- **Contrast**: Analytical, comparative

## Real-World Use Cases

### 1. Creative Writing Inspiration

**Setup:**
```json
{
  "reasoning_strategies": {
    "free_association": 0.4,
    "creative_what_if": 0.3,
    "analogical_reasoning": 0.2,
    "exploration": 0.1
  },
  "dream_interval": 8,
  "max_thoughts_per_session": 30
}
```

**Usage:**
- Start dreaming with creative seed
- Review golden thoughts for story ideas
- Export interesting threads for development

### 2. Research Brainstorming

**Setup:**
```json
{
  "enable_web_search": true,
  "reasoning_strategies": {
    "logical_deduction": 0.3,
    "pattern_recognition": 0.3,
    "synthesis": 0.2,
    "exploration": 0.2
  }
}
```

**Usage:**
- Dream on specific research topics
- Web search brings in current research
- Analyze patterns across sessions

### 3. Philosophical Exploration

**Setup:**
```json
{
  "reasoning_strategies": {
    "meta_cognition": 0.3,
    "analogical_reasoning": 0.25,
    "free_association": 0.25,
    "synthesis": 0.2
  },
  "dream_interval": 12
}
```

**Usage:**
- Long, contemplative sessions
- Focus on golden thoughts
- Build philosophical frameworks over time

### 4. Problem Solving

**Setup:**
```json
{
  "reasoning_strategies": {
    "logical_deduction": 0.35,
    "analogical_reasoning": 0.25,
    "creative_what_if": 0.2,
    "pattern_recognition": 0.2
  },
  "enable_branching": true
}
```

**Usage:**
- Seed with problem statement
- Let AI explore solution space
- Review all branches for insights

### 5. Learning and Education

**Setup:**
```json
{
  "enable_web_search": true,
  "reasoning_strategies": {
    "pattern_recognition": 0.3,
    "synthesis": 0.25,
    "meta_cognition": 0.2,
    "exploration": 0.25
  }
}
```

**Usage:**
- Dream on subjects you're learning
- AI makes connections between concepts
- Export thoughts as study notes

## Troubleshooting

### Issue: "Connection refused" error

**Cause:** Ollama not running

**Solution:**
```bash
# Start Ollama
ollama serve

# In another terminal
python3 dreaming_ai.py
```

### Issue: Slow thought generation

**Causes:**
1. Large model
2. Web search enabled
3. Short dream_interval

**Solutions:**
```json
{
  "model": "qwen2.5:0.5b",  // Use smaller model
  "enable_web_search": false,  // Disable web search
  "dream_interval": 5  // Increase interval
}
```

### Issue: Low-quality thoughts

**Causes:**
1. Model too small
2. Poor seed selection
3. Insufficient context

**Solutions:**
```json
{
  "model": "gemma2:2b",  // Upgrade model
  "max_thoughts_per_session": 50  // Longer sessions build context
}
```

### Issue: Database locked

**Cause:** Multiple instances accessing same database

**Solution:**
```bash
# Use different databases for concurrent sessions
python3 dreaming_ai.py --config config1.json
# config1.json: "db_path": "dreams1.db"

python3 dreaming_ai.py --config config2.json
# config2.json: "db_path": "dreams2.db"
```

### Issue: No golden thoughts found

**Causes:**
1. Interest threshold too high
2. Short sessions
3. Model not generating interesting content

**Solutions:**
```json
{
  "interest_threshold": 0.3,  // Lower threshold
  "max_thoughts_per_session": 100,  // Longer sessions
  "reasoning_strategies": {
    "creative_what_if": 0.3,  // More creative modes
    "exploration": 0.2
  }
}
```

### Issue: Out of memory

**Causes:**
1. Model too large for system
2. Too many thoughts in session

**Solutions:**
```json
{
  "model": "qwen2.5:0.5b",  // Smaller model
  "max_thoughts_per_session": 30  // Shorter sessions
}
```

## FAQ

### Q: How long should a dreaming session be?

**A:** Depends on your goal:
- **Quick exploration**: 20-30 thoughts (5-10 minutes)
- **Standard session**: 50-100 thoughts (15-30 minutes)
- **Deep dive**: 200+ thoughts (1+ hour)

### Q: Can I run multiple sessions simultaneously?

**A:** Yes! Use different config files with different database paths:
```bash
# Terminal 1
python3 dreaming_ai.py --config config_creative.json --auto-start

# Terminal 2
python3 dreaming_ai.py --config config_analytical.json --auto-start
```

### Q: How do I seed with a specific topic?

**A:** Currently, seeds are random. For topic-specific dreaming:
1. Modify `ThoughtSeeder` class to accept custom seeds
2. Or manually create first thought in database
3. Or wait for future update with custom seed support

### Q: What's the best model for dreaming?

**A:**
- **Best overall**: gemma2:2b (balanced speed/quality)
- **Fastest**: qwen2.5:0.5b
- **Highest quality**: llama3:8b (if you have the RAM)

### Q: Can I disable the console output?

**A:** Yes:
```bash
python3 dreaming_ai.py --quiet --auto-start
```

Or in Python:
```python
ai = DreamingAI(verbose=False)
```

### Q: How much disk space does the database use?

**A:** Approximately:
- 1 thought ≈ 500 bytes
- 1000 thoughts ≈ 500 KB
- 100,000 thoughts ≈ 50 MB

Very reasonable for long-term use.

### Q: Can I train on golden thoughts?

**A:** Not directly, but you can:
1. Export golden thoughts
2. Use them as fine-tuning data
3. Or as few-shot examples for other models

### Q: Is internet required?

**A:** Only if web search is enabled. Otherwise, fully offline.

### Q: Can I use GPT-4 or Claude instead of Ollama?

**A:** Currently only Ollama is supported. Future versions may support:
- OpenAI API
- Anthropic Claude API
- Local transformers

### Q: How do I contribute?

**A:**
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

Areas needing help:
- Additional reasoning modes
- Better visualization
- Multi-agent interactions
- Alternative LLM backends

## Advanced Topics

### Custom Reasoning Modes

Create your own reasoning style:

```python
from dreaming_ai import ReasoningEngine

class MyReasoningEngine(ReasoningEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reasoning_modes.append('poetic')

    def _build_prompt(self, context, mode, web_context=""):
        if mode == 'poetic':
            return f"{context}\n\nExpress this thought poetically..."
        return super()._build_prompt(context, mode, web_context)
```

### Integration with Other Tools

**Jupyter Notebook:**
```python
from dreaming_ai import DreamingAI
import matplotlib.pyplot as plt

ai = DreamingAI(verbose=False)
# ... generate thoughts ...

# Visualize in notebook
thoughts = ai.memory.get_all_thoughts()
scores = [t.interest_score for t in thoughts]
plt.plot(scores)
plt.show()
```

**Web Dashboard:**
```python
from flask import Flask, jsonify
from dreaming_ai import DreamingAI

app = Flask(__name__)
ai = DreamingAI(verbose=False)

@app.route('/golden')
def get_golden():
    thoughts = ai.memory.get_golden_thoughts(limit=10)
    return jsonify(thoughts)
```

## Resources

### Further Reading

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Architecture Design](Multi-Agent Thinking System Architecture Design.md)
- [Deployment Guide](DreamingAI Deployment Guide.md)

### Community

- GitHub Issues: Report bugs and request features
- Discussions: Share your dreaming sessions
- Examples: See what others have discovered

### Support

For help:
1. Check this guide
2. Check FAQ section
3. Review API documentation
4. Search existing GitHub issues
5. Create new issue with details

## Conclusion

DreamingAI is a powerful tool for autonomous reasoning and creative exploration. Experiment with different configurations, explore the golden thoughts, and discover what your AI dreams about!

Happy dreaming! 🌙✨

---

**Version:** 2.0.0
**Last Updated:** 2024
**License:** MIT
