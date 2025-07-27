# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DreamingAI is an autonomous reasoning system that runs continuous thought loops on local language models without requiring user prompts. The system generates self-directed thought chains, discovers insights, and identifies valuable patterns through pure autonomous thinking.

## Architecture

The system is built as a single-file Python application (`dreaming_ai.py`) with a modular class-based architecture:

- **DreamingAI**: Main orchestrator class that coordinates all components
- **ThoughtSeeder**: Generates initial thinking seeds from abstract/concrete concepts and questions
- **ReasoningEngine**: Processes thoughts through different reasoning modes (free association, logical deduction, creative what-if, pattern recognition, analogical reasoning)
- **InterestDetector**: Analyzes thoughts to calculate interest scores and identify "golden strike" discoveries
- **MemorySystem**: Manages short-term (in-memory) and long-term (SQLite) storage of thoughts
- **OutputManager**: Handles console display, file output, and session summaries

## Development Commands

### Local Development
```bash
# Install dependencies
pip install requests

# Start Ollama service (required)
ollama serve

# Download recommended model
ollama pull gemma2:2b

# Run the application
python3 dreaming_ai.py
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build/run manually
docker build -t dreaming-ai .
docker run -it -p 11434:11434 dreaming-ai
```

### Application Commands
Within the running application:
- `1` or `start` - Begin autonomous dreaming session
- `2` or `golden` - Display discovered golden thoughts
- `3`, `quit`, or `exit` - Exit application

## Configuration

The application uses `config.json` for configuration:
- `model`: Ollama model to use (default: "qwen2.5:0.5b")
- `ollama_url`: Ollama API endpoint
- `dream_interval`: Seconds between thoughts (default: 8)
- `max_thoughts_per_session`: Maximum thoughts per session (default: 50)
- `interest_threshold`: Threshold for marking thoughts as interesting (default: 0.4)
- `reasoning_strategies`: Weights for different reasoning modes

## Key Dependencies

- **Ollama**: Local LLM runtime (must be running on port 11434)
- **requests**: HTTP client for Ollama API communication
- **sqlite3**: Built-in database for thought persistence
- **Standard library**: pathlib, dataclasses, typing, datetime, json, threading, logging, random, time

## Data Storage

- `dreaming_memory.db`: SQLite database containing all thoughts and golden discoveries
- `dream_outputs/`: Directory for session outputs
  - `golden_thought_*.md`: Individual golden discoveries
  - `session_summary_*.md`: Session summaries
  - `dreaming.log`: Application logs

## Reasoning Modes

The system employs five distinct reasoning approaches:
1. **Free Association**: Natural mind wandering
2. **Logical Deduction**: Step-by-step logical reasoning
3. **Creative What-If**: Hypothetical scenario exploration
4. **Pattern Recognition**: Finding connections between ideas
5. **Analogical Reasoning**: Drawing parallels with other concepts

## Interest Detection

Thoughts are scored based on:
- Discovery keywords ("connection", "pattern", "insight", etc.)
- Gold strike indicators ("breakthrough", "eureka", "profound", etc.)
- Content complexity and length
- Question marks (curiosity) and exclamation marks (excitement)

Thoughts scoring above 0.6 or containing gold strike indicators are marked as "golden thoughts" and specially preserved.

## New Enhanced Components

### Multi-Agent System (`multi_agent_system.py`)
- Creates multiple AI agents with unique personalities and conversation styles
- Agents engage in autonomous conversations without system prompts
- Personality traits: curious, analytical, creative, methodical, intuitive, etc.
- Conversation styles: questioning, storytelling, technical, metaphorical, etc.
- Stores conversations in `multi_agent_memory.db`

### Web Monitoring Interface (`web_monitor.py`)
- Flask-based web interface at http://localhost:8080
- Real-time conversation monitoring and statistics
- Agent profiles and conversation history
- Auto-refreshing dashboard with live updates
- REST API endpoints for integration

### GUI Visualizer (`gui_visualizer.py`)
- Tkinter-based real-time conversation visualizer
- Color-coded agent messages and personality displays
- **API Configuration Box**: Enter localhost Ollama API URL
- **AI-Generated Highlights**: Analyze conversations for key insights
- Export capabilities and conversation replay
- Live monitoring with threading support

### Web Search Integration (`web_search_agent.py`)
- Adds web search capabilities to thinking processes
- Generates search queries from conversation context
- Integrates search results into agent reasoning
- Mock implementation ready for real search API integration

### Demo Launcher (`demo_system.py`)
- Comprehensive demo system with GUI launcher
- System health checks and component testing
- One-click launching of all system components
- Process management and status monitoring
- Browser auto-opening for web interfaces

## Enhanced Features

### API Configuration
- GUI includes configurable Ollama API URL field
- Connection testing with model detection
- Support for localhost and custom endpoints
- Real-time connection status indicators

### AI-Generated Highlights
- Analyze conversations using local LLM
- Extract key insights, discoveries, and patterns
- Save highlights to timestamped files
- Progress indication during generation

## Development Commands (Updated)

### Quick Start Demo
```bash
# Launch complete demo system
python3 demo_system.py
```

### Individual Components
```bash
# Original single-agent dreaming
python3 dreaming_ai.py

# Multi-agent conversations
python3 multi_agent_system.py

# GUI visualizer with API config
python3 gui_visualizer.py

# Web monitoring interface
python3 web_monitor.py

# Web search demonstration
python3 web_search_agent.py
```

### Docker Usage (Enhanced)
```bash
# Build with multi-model support
docker-compose up --build

# Access interfaces:
# - Ollama API: http://localhost:11434
# - Web Monitor: http://localhost:8080
```

## Configuration Files

- `config.json`: Original dreaming AI settings
- `multi_agent_config.json`: Multi-agent system configuration
- API URLs configurable through GUI interface
- Persistent model storage in Docker volumes

## Data Storage (Enhanced)

- `dreaming_memory.db`: Original single-agent thoughts
- `multi_agent_memory.db`: Multi-agent conversations and profiles
- `dream_outputs/`: Session summaries and golden thoughts
- `highlights_*.txt`: AI-generated conversation highlights
- `conversation_export_*.txt`: Exported conversation logs

## System Requirements

- Python 3.8+
- Ollama with models (gemma2:2b, qwen2.5:1.5b, phi3:mini recommended)
- 4GB+ RAM for Docker deployment
- tkinter for GUI (usually included with Python)
- flask, requests for web components

## No Traditional Testing

This is a creative/experimental AI system focused on autonomous reasoning rather than deterministic functionality. The `demo_system.py` includes basic system health checks, but the system's value is measured by the quality and interestingness of generated thoughts and conversations.