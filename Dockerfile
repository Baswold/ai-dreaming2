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

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama in background\n\
ollama serve &\n\
sleep 5\n\
\n\
# Pull the model if not exists\n\
if ! ollama list | grep -q "gemma2:2b"; then\n\
    echo "Downloading gemma2:2b model..."\n\
    ollama pull gemma2:2b\n\
fi\n\
\n\
# Start DreamingAI\n\
python3 dreaming_ai.py\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]

