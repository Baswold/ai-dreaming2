# DreamingAI

DreamingAI is an experimental autonomous reasoning system that runs on local language models. It can launch multiple agents, monitor them via a web interface, and visualize conversations in a Tkinter GUI.

## Requirements
- Python 3.8+
- [Ollama](https://github.com/jmorganca/ollama) for running local models
- `requests`, `flask`, `websocket-client`, `requests-html` (see `requirements.txt`)
- `python3-tk` (OS package) if you want to use the GUI components

Tkinter itself ships with Python, but many Linux distributions provide the GUI bindings in a separate package called `python3-tk`. Install it via your package manager (e.g. `apt-get install python3-tk` on Debian/Ubuntu) if the GUI visualizer fails to launch.

## Running
1. Ensure Ollama is running and you have pulled a compatible model.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the demo:
   ```bash
   python3 demo_system.py
   ```
