FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip3 install requests

# Create output directory
RUN mkdir -p dream_outputs

# Expose Ollama port
EXPOSE 11434

# Install additional dependencies for GUI and web interface
RUN apt-get update && apt-get install -y \
    python3-tk \
    firefox \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install flask websocket-client requests-html

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama in background\n\
ollama serve &\n\
sleep 10\n\
\n\
# Pull multiple models for multi-agent conversations\n\
models=("gemma2:2b" "qwen2.5:1.5b" "phi3:mini")\n\
for model in "${models[@]}"; do\n\
    if ! ollama list | grep -q "$model"; then\n\
        echo "Downloading $model model..."\n\
        ollama pull "$model"\n\
    fi\n\
done\n\
\n\
# Start web monitoring interface in background\n\
python3 web_monitor.py &\n\
\n\
# Start DreamingAI\n\
python3 dreaming_ai.py\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]

