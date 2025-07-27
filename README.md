# DreamingAI

DreamingAI is an experimental autonomous reasoning system that allows a local language model to "dream" on its own. The application runs continuous reasoning loops without any user prompts or tasks. Ideas emerge organically, interesting thoughts are captured, and breakthrough "golden" discoveries are stored for later review.

## Features

- **Promptless thinking** – the AI starts with a completely blank slate and develops its own train of thought.
- **Multiple reasoning strategies** – free association, logical deduction, creative "what if" speculation, pattern recognition and analogical reasoning.
- **Interest detection** – automatically identifies interesting thoughts and flags potential "gold strikes".
- **Memory system** – short term context and an SQLite database for long‑term storage of ideas.
- **Local model support** – works with [Ollama](https://ollama.ai) and is optimised for small models that can run on modest hardware.

See `DreamingAI - Autonomous Reasoning System.md` for a deeper explanation of the philosophy and inner workings.

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

## Repository Contents

- `dreaming_ai.py` – main application
- `config.json` – default configuration
- `Dockerfile` / `docker-compose.yml` – container setup
- `requirements.txt` – Python dependencies
- `DreamingAI - Autonomous Reasoning System.md` – full system overview
- `DreamingAI Deployment Guide.md` – deployment and usage notes
- `Multi-Agent Thinking System Architecture Design.md` – notes on a possible multi-agent extension

## License

This project is released under the MIT license. See the source files for details.
