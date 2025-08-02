# AI Code Assistant Docker Image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    python3-dev \
    nodejs \
    npm \
    curl \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Mermaid CLI for flowcharts
RUN npm install -g @mermaid-js/mermaid-cli

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static/flowcharts logs uploads

# Expose ports (FastAPI: 8000, Streamlit: 8501)
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]