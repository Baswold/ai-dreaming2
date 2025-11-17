# DreamingAI API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Data Models](#data-models)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)
7. [Extension Guide](#extension-guide)

## Overview

DreamingAI is a comprehensive autonomous reasoning system that allows AI models to "dream" and explore ideas independently. This documentation covers all classes, methods, and configuration options.

### Architecture

```
DreamingAI (Main Orchestrator)
├── ThoughtSeeder (Generate initial seeds)
├── ReasoningEngine (Generate thoughts)
│   └── WebSearchEngine (Web search integration)
├── InterestDetector (Evaluate thought quality)
├── MemorySystem (Short & long-term storage)
│   └── SQLite Database
├── ThoughtAnalyzer (Pattern analysis)
└── OutputManager (Display & export)
```

## Data Models

### Thought

Primary data structure representing a single thought in the reasoning chain.

```python
@dataclass
class Thought:
    id: str                          # Unique identifier
    timestamp: datetime              # When thought was created
    content: str                     # Thought content
    thought_type: str               # Type: seed, reasoning, gold_strike, etc.
    parent_id: Optional[str]        # Parent thought ID
    interest_score: float           # 0.0-1.0 interest rating
    tags: List[str]                 # Categorization tags
    metadata: Dict                  # Additional metadata
    branch_id: Optional[str]        # Branch identifier
    web_sources: List[str]          # URLs if web-informed
```

**Thought Types:**
- `seed`: Initial thought that starts a session
- `reasoning`: Standard reasoning thought
- `web_search`: Thought informed by web search
- `gold_strike`: Highly interesting discovery
- `synthesis`: Synthesized from multiple thoughts
- `branch`: Divergent thinking branch
- `insight`: Notable insight
- `meta_cognition`: Reflection on thinking process

### ThoughtBranch

Represents a divergent branch in the reasoning tree.

```python
@dataclass
class ThoughtBranch:
    id: str                         # Unique branch ID
    parent_thought_id: str          # ID of branching point
    created_at: datetime            # Creation timestamp
    thoughts: List[Thought]         # Thoughts in this branch
    theme: str                      # Branch theme/topic
    active: bool                    # Whether branch is active
```

## Core Classes

### ThoughtSeeder

Generates initial seeds and prompts for autonomous reasoning.

```python
class ThoughtSeeder:
    def __init__(self)

    def generate_seed(self, seed_type: str = None) -> str
```

**Methods:**

- `generate_seed(seed_type=None)`: Generate a random or specific type of seed
  - **Parameters:**
    - `seed_type` (str, optional): Type of seed to generate
      - `'combination'`: Combines two concepts
      - `'abstract_question'`: Philosophical question
      - `'philosophical'`: Philosophical prompt + concept
      - `'contrast'`: Contrasts two concepts
      - `'metaphor'`: Creates a metaphor
      - `'timestamp_based'`: Time-based reflection
  - **Returns:** String containing the seed thought

**Example:**
```python
seeder = ThoughtSeeder()
seed = seeder.generate_seed(seed_type='metaphor')
# Output: "If consciousness were a river, what would it look like?"
```

### WebSearchEngine

Handles web searches with caching for enriching reasoning with external knowledge.

```python
class WebSearchEngine:
    def __init__(self, cache_ttl: int = 3600, max_results: int = 3)

    def search(self, query: str) -> List[Dict]
    def extract_search_worthy_terms(self, text: str) -> List[str]
    def format_search_results(self, results: List[Dict]) -> str
```

**Methods:**

- `search(query)`: Perform web search with caching
  - **Parameters:**
    - `query` (str): Search query
  - **Returns:** List of search result dictionaries
  - **Cache:** Results cached for `cache_ttl` seconds

- `extract_search_worthy_terms(text)`: Extract searchable terms from text
  - **Parameters:**
    - `text` (str): Text to analyze
  - **Returns:** List of extracted terms

- `format_search_results(results)`: Format results for LLM consumption
  - **Parameters:**
    - `results` (List[Dict]): Search results
  - **Returns:** Formatted string

**Example:**
```python
web_search = WebSearchEngine(cache_ttl=1800, max_results=5)
results = web_search.search("quantum computing")
formatted = web_search.format_search_results(results)
```

### ReasoningEngine

Core reasoning engine that generates thoughts using various reasoning modes.

```python
class ReasoningEngine:
    def __init__(self, ollama_url: str, model: str,
                 web_search_engine: Optional[WebSearchEngine] = None)

    def generate_thought(self, context: List[Thought], mode: str = None,
                        enable_web_search: bool = False) -> Tuple[str, List[str]]
    def get_performance_summary(self) -> Dict
```

**Reasoning Modes:**
- `free_association`: Unstructured creative thinking
- `logical_deduction`: Step-by-step logical reasoning
- `creative_what_if`: Imaginative speculation
- `pattern_recognition`: Identify patterns in ideas
- `analogical_reasoning`: Reason by analogy
- `meta_cognition`: Reflect on thinking process
- `synthesis`: Combine multiple ideas
- `exploration`: Explore adjacent concepts
- `web_informed`: Use web search results

**Methods:**

- `generate_thought(context, mode=None, enable_web_search=False)`:
  - **Parameters:**
    - `context` (List[Thought]): Recent thoughts for context
    - `mode` (str, optional): Specific reasoning mode
    - `enable_web_search` (bool): Whether to use web search
  - **Returns:** Tuple of (thought_content, web_sources)
  - **Retry Logic:** Automatically retries up to 3 times with exponential backoff

- `get_performance_summary()`:
  - **Returns:** Dictionary with performance statistics
    - `total_requests`: Total API calls made
    - `successful_requests`: Successful calls
    - `failed_requests`: Failed calls
    - `avg_latency`: Average response time

**Example:**
```python
engine = ReasoningEngine(
    ollama_url="http://localhost:11434",
    model="gemma2:2b",
    web_search_engine=web_search
)

context = [previous_thought1, previous_thought2]
content, sources = engine.generate_thought(
    context,
    mode='meta_cognition',
    enable_web_search=True
)
```

### InterestDetector

Evaluates thought quality and identifies particularly interesting thoughts.

```python
class InterestDetector:
    def __init__(self)

    def calculate_interest_score(self, thought: str,
                                context: List[Thought] = None) -> float
    def is_gold_strike(self, thought: str, score: float) -> bool
```

**Scoring Factors:**
- Interest keywords (0.1 each)
- Gold strike indicators (0.5 each)
- Semantic relationships (0.15 each)
- Length bonus (0.1-0.2)
- Question marks (0.05 each, max 0.15)
- Exclamation marks (0.1 each, max 0.2)
- Novelty vs context (up to 0.2)

**Methods:**

- `calculate_interest_score(thought, context=None)`:
  - **Parameters:**
    - `thought` (str): Thought content to evaluate
    - `context` (List[Thought], optional): Recent thoughts for novelty detection
  - **Returns:** Float between 0.0 and 1.0

- `is_gold_strike(thought, score)`:
  - **Parameters:**
    - `thought` (str): Thought content
    - `score` (float): Pre-calculated interest score
  - **Returns:** Boolean indicating if thought is a "golden" discovery

**Example:**
```python
detector = InterestDetector()
score = detector.calculate_interest_score(
    "This breakthrough reveals a fundamental pattern!",
    context=[thought1, thought2]
)
is_golden = detector.is_gold_strike(thought_content, score)
```

### MemorySystem

Manages both short-term and long-term memory using SQLite.

```python
class MemorySystem:
    def __init__(self, db_path: str = "dreaming_memory.db")

    def add_thought(self, thought: Thought)
    def add_golden_thought(self, thought: Thought, context: str = "")
    def create_branch(self, parent_thought: Thought, theme: str = "") -> ThoughtBranch
    def get_recent_thoughts(self, limit: int = 10) -> List[Thought]
    def get_golden_thoughts(self, limit: int = None) -> List[Dict]
    def get_all_thoughts(self, limit: int = None) -> List[Thought]
    def save_session(self, session_id: str, start_time: datetime,
                    end_time: datetime, thoughts: List[Thought], summary: str)
```

**Database Schema:**

```sql
-- Thoughts table
CREATE TABLE thoughts (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    content TEXT,
    thought_type TEXT,
    parent_id TEXT,
    interest_score REAL,
    tags TEXT,
    metadata TEXT,
    branch_id TEXT,
    web_sources TEXT
);

-- Golden thoughts table
CREATE TABLE golden_thoughts (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    content TEXT,
    interest_score REAL,
    discovery_context TEXT,
    web_sources TEXT
);

-- Thought branches table
CREATE TABLE thought_branches (
    id TEXT PRIMARY KEY,
    parent_thought_id TEXT,
    created_at TEXT,
    theme TEXT,
    active INTEGER
);

-- Sessions table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    start_time TEXT,
    end_time TEXT,
    total_thoughts INTEGER,
    golden_thoughts INTEGER,
    avg_interest_score REAL,
    summary TEXT
);
```

**Example:**
```python
memory = MemorySystem(db_path="my_dreams.db")

# Add a thought
thought = Thought(id="t1", timestamp=datetime.now(), ...)
memory.add_thought(thought)

# Get recent thoughts
recent = memory.get_recent_thoughts(limit=5)

# Create a branch
branch = memory.create_branch(parent_thought, theme="exploration")
```

### ThoughtAnalyzer

Analyzes thought patterns, clusters thoughts, and extracts themes.

```python
class ThoughtAnalyzer:
    def __init__(self)

    def cluster_thoughts(self, thoughts: List[Thought],
                        n_clusters: int = 5) -> Dict[int, List[Thought]]
    def extract_themes(self, thoughts: List[Thought],
                      top_n: int = 10) -> List[Tuple[str, int]]
    def analyze_interest_evolution(self, thoughts: List[Thought]) -> Dict
```

**Methods:**

- `cluster_thoughts(thoughts, n_clusters=5)`:
  - Uses TF-IDF vectorization and K-means clustering
  - **Returns:** Dictionary mapping cluster ID to list of thoughts

- `extract_themes(thoughts, top_n=10)`:
  - Performs word frequency analysis with stop word filtering
  - **Returns:** List of (word, count) tuples

- `analyze_interest_evolution(thoughts)`:
  - Analyzes how interest scores change over time
  - **Returns:** Dictionary with mean, std, min, max, trend

**Example:**
```python
analyzer = ThoughtAnalyzer()

# Cluster thoughts
clusters = analyzer.cluster_thoughts(all_thoughts, n_clusters=3)
for cluster_id, cluster_thoughts in clusters.items():
    print(f"Cluster {cluster_id}: {len(cluster_thoughts)} thoughts")

# Extract themes
themes = analyzer.extract_themes(all_thoughts, top_n=5)
for word, count in themes:
    print(f"{word}: {count}")

# Analyze evolution
stats = analyzer.analyze_interest_evolution(all_thoughts)
print(f"Average interest: {stats['mean']:.2f}")
```

### OutputManager

Manages display, saving, and exporting of thoughts and discoveries.

```python
class OutputManager:
    def __init__(self, output_dir: str = "dream_outputs", verbose: bool = True)

    def display_thought(self, thought: Thought)
    def save_golden_thought(self, thought: Thought)
    def generate_session_summary(self, thoughts: List[Thought],
                                 performance_stats: Dict = None) -> str
    def export_to_json(self, thoughts: List[Thought], filename: str)
    def create_visualization(self, thoughts: List[Thought], filename: str)
```

**Visualization Features:**
- Interest score over time (line plot)
- Thought type distribution (bar chart)
- Interest score distribution (histogram)
- Thought length over time (scatter plot)

**Example:**
```python
output = OutputManager(output_dir="my_outputs", verbose=True)

# Display thought in real-time
output.display_thought(thought)

# Save golden thought
output.save_golden_thought(golden_thought)

# Generate summary
summary = output.generate_session_summary(session_thoughts)

# Export to JSON
output.export_to_json(all_thoughts, "export.json")

# Create visualizations
output.create_visualization(all_thoughts, "analysis.png")
```

### DreamingAI

Main orchestrator class that coordinates all components.

```python
class DreamingAI:
    def __init__(self, config_path: str = "config.json", verbose: bool = True)

    def start_dreaming(self, max_thoughts: int = None)
    def stop_dreaming(self)
    def show_golden_thoughts(self, limit: int = 10)
    def analyze_thoughts(self)
    def export_data(self, format: str = 'json')
```

**Methods:**

- `start_dreaming(max_thoughts=None)`:
  - Starts autonomous dreaming session
  - **Parameters:**
    - `max_thoughts` (int, optional): Override config max thoughts

- `stop_dreaming()`:
  - Stops dreaming and generates session summary

- `show_golden_thoughts(limit=10)`:
  - Displays top golden thoughts from database

- `analyze_thoughts()`:
  - Performs comprehensive analysis of all thoughts
  - Includes clustering, theme extraction, and visualization

- `export_data(format='json')`:
  - Exports all thoughts in specified format

**Example:**
```python
ai = DreamingAI(config_path="config.json", verbose=True)

# Start dreaming
ai.start_dreaming(max_thoughts=50)

# View golden thoughts
ai.show_golden_thoughts(limit=5)

# Analyze patterns
ai.analyze_thoughts()

# Export data
ai.export_data(format='json')
```

## Configuration

### Configuration File Format

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

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | "gemma2:2b" | Ollama model name |
| `ollama_url` | string | "http://localhost:11434" | Ollama API URL |
| `db_path` | string | "dreaming_memory.db" | Database file path |
| `output_dir` | string | "dream_outputs" | Output directory |
| `reasoning_strategies` | object | See above | Probability distribution of reasoning modes |
| `interest_threshold` | float | 0.4 | Minimum score for "interesting" thoughts |
| `dream_interval` | int | 5 | Seconds between thoughts |
| `max_thoughts_per_session` | int | 100 | Max thoughts per session |
| `enable_web_search` | boolean | true | Enable web search integration |
| `web_search_cache_ttl` | int | 3600 | Web search cache TTL (seconds) |
| `web_search_max_results` | int | 3 | Max web search results |
| `enable_branching` | boolean | false | Enable thought branching |
| `branch_probability` | float | 0.1 | Probability of creating branch |

## Usage Examples

### Basic Usage

```python
from dreaming_ai import DreamingAI

# Initialize with default config
ai = DreamingAI()

# Start dreaming
ai.start_dreaming()
```

### Command Line Usage

```bash
# Basic start
python3 dreaming_ai.py

# Auto-start with 50 thoughts
python3 dreaming_ai.py --auto-start --max-thoughts 50

# Analyze existing thoughts
python3 dreaming_ai.py --analyze

# Export data
python3 dreaming_ai.py --export json

# Quiet mode
python3 dreaming_ai.py --quiet --auto-start
```

### Programmatic Usage

```python
from dreaming_ai import DreamingAI, Thought
from datetime import datetime

# Initialize
ai = DreamingAI(config_path="custom_config.json")

# Manually create and process a thought
manual_thought = Thought(
    id="manual_1",
    timestamp=datetime.now(),
    content="What if we could dream in code?",
    thought_type="seed"
)
ai._process_thought(manual_thought)

# Start automated dreaming
ai.start_dreaming(max_thoughts=20)

# Analyze results
ai.analyze_thoughts()

# Export
ai.export_data(format='json')
```

### Web Search Integration

```python
from dreaming_ai import DreamingAI

# Create config with web search enabled
config = {
    "enable_web_search": True,
    "web_search_max_results": 5,
    "max_thoughts_per_session": 30
}

# Initialize
ai = DreamingAI()
ai.config.update(config)

# Web search will automatically integrate into reasoning
ai.start_dreaming()
```

### Custom Reasoning Pipeline

```python
from dreaming_ai import (
    ThoughtSeeder, ReasoningEngine, InterestDetector,
    MemorySystem, Thought
)
from datetime import datetime

# Initialize components
seeder = ThoughtSeeder()
engine = ReasoningEngine(ollama_url="http://localhost:11434", model="gemma2:2b")
detector = InterestDetector()
memory = MemorySystem()

# Generate seed
seed_content = seeder.generate_seed(seed_type='metaphor')
seed = Thought(
    id="custom_seed",
    timestamp=datetime.now(),
    content=seed_content,
    thought_type="seed"
)
memory.add_thought(seed)

# Generate follow-up thoughts
for i in range(5):
    context = memory.get_recent_thoughts(5)
    content, sources = engine.generate_thought(context, mode='creative_what_if')

    thought = Thought(
        id=f"custom_{i}",
        timestamp=datetime.now(),
        content=content,
        thought_type="reasoning",
        parent_id=context[-1].id if context else None
    )

    # Score and save
    thought.interest_score = detector.calculate_interest_score(content, context)
    memory.add_thought(thought)

    if detector.is_gold_strike(content, thought.interest_score):
        memory.add_golden_thought(thought, "Custom pipeline discovery")
```

## Extension Guide

### Creating Custom Reasoning Modes

```python
from dreaming_ai import ReasoningEngine

class CustomReasoningEngine(ReasoningEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reasoning_modes.append('custom_mode')

    def _build_prompt(self, context: str, mode: str, web_context: str = "") -> str:
        if mode == 'custom_mode':
            return f"{context}\n\nApply custom reasoning approach..."
        return super()._build_prompt(context, mode, web_context)
```

### Custom Interest Detection

```python
from dreaming_ai import InterestDetector

class CustomInterestDetector(InterestDetector):
    def calculate_interest_score(self, thought: str, context=None) -> float:
        # Start with base score
        score = super().calculate_interest_score(thought, context)

        # Add custom scoring logic
        if "custom_keyword" in thought.lower():
            score += 0.3

        return min(score, 1.0)
```

### Custom Output Formats

```python
from dreaming_ai import OutputManager
import csv

class CustomOutputManager(OutputManager):
    def export_to_csv(self, thoughts, filename="export.csv"):
        """Export thoughts to CSV"""
        with open(self.output_dir / filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Timestamp', 'Content', 'Type', 'Score'])

            for t in thoughts:
                writer.writerow([
                    t.id,
                    t.timestamp.isoformat(),
                    t.content,
                    t.thought_type,
                    t.interest_score
                ])
```

## Performance Optimization

### Database Optimization

```python
# Use connection pooling for high-volume operations
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Create indexes for faster queries
conn = sqlite3.connect("dreaming_memory.db")
conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON thoughts(timestamp)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_interest_score ON thoughts(interest_score)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON thoughts(thought_type)")
conn.close()
```

### Caching Strategies

```python
from functools import lru_cache

class OptimizedReasoningEngine(ReasoningEngine):
    @lru_cache(maxsize=128)
    def _build_prompt_cached(self, context_hash: str, mode: str) -> str:
        # Cache prompt building for repeated contexts
        return self._build_prompt(context, mode)
```

## Error Handling

### Graceful Degradation

The system includes comprehensive error handling:

```python
# Automatic retry with exponential backoff
for attempt in range(self.max_retries):
    try:
        response = requests.post(...)
        if response.status_code == 200:
            return result
    except requests.exceptions.Timeout:
        if attempt < self.max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

# Fallback thoughts when API fails
fallback_thoughts = [
    "I notice something interesting about the nature of thought itself...",
    "In this moment of silence, new possibilities emerge..."
]
return random.choice(fallback_thoughts), []
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python3 test_dreaming_ai.py

# Run specific test case
python3 -m unittest test_dreaming_ai.TestInterestDetector

# Run with verbose output
python3 -m unittest test_dreaming_ai -v
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check URL in config matches Ollama instance

2. **Web Search Not Working**
   - Install duckduckgo-search: `pip install duckduckgo-search`
   - Check internet connection
   - Verify `enable_web_search: true` in config

3. **Database Locked**
   - Close other connections to database
   - Use separate database files for concurrent sessions

4. **Memory Issues**
   - Reduce `max_thoughts_per_session`
   - Increase `dream_interval` to reduce API load
   - Limit short-term memory size

## License

MIT License - See source files for details.

## Contributing

Contributions welcome! Areas for enhancement:
- Additional reasoning modes
- Alternative LLM backends
- Advanced visualization techniques
- Multi-agent interactions
- Real-time collaboration features

---

**Version:** 2.0.0
**Last Updated:** 2024
**Maintainer:** DreamingAI Development Team
