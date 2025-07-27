# DreamingAI at a Glance

DreamingAI is an experimental system that lets a local language model "dream" autonomously. It generates thought chains, tracks interesting ideas and stores notable "golden" discoveries for later review.

## Key Features
- Promptless reasoning loops that start from a blank slate
- Multiple thinking strategies such as free association and logical deduction
- Interest detection to highlight valuable insights
- SQLite-based memory for long‑term storage
- Works with the local [Ollama](https://ollama.ai) LLM framework

## Repository Highlights
- `dreaming_ai.py` – main Python application
- `config.json` – configuration with model and runtime options
- `Dockerfile` and `docker-compose.yml` – containerized setup
- `DreamingAI - Autonomous Reasoning System.md` – overview and philosophy
- `DreamingAI Deployment Guide.md` – instructions for running the project

## Quick Start
1. Install Ollama and pull a small model (e.g. `qwen2.5:0.5b`)
2. Install Python requirements with `pip install -r requirements.txt`
3. Run `python3 dreaming_ai.py` and choose **start** to begin a session

Golden thoughts and summaries are saved under `dream_outputs/` and stored in `dreaming_memory.db`.
