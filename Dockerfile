# AI-Powered Media Library Organizer - Production Docker Image
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Media Organizer Team"
LABEL description="AI-powered media library organizer using Google Gemini"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r organizer && useradd -r -g organizer organizer

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env.example ./
COPY README.md ./
COPY LICENSE ./

# Create directories for data and configuration
RUN mkdir -p /app/data /app/config /app/logs && \
    chown -R organizer:organizer /app

# Create volume mount points
VOLUME ["/media", "/app/config", "/app/logs"]

# Switch to non-root user
USER organizer

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 src/main.py test || exit 1

# Default environment file location
ENV ENV_FILE=/app/config/.env

# Entry point script
COPY --chown=organizer:organizer docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["--help"]
