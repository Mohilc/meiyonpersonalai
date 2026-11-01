# Use official lightweight Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs as user ID 1000 for container security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY --chown=appuser:appuser . .

# Ensure data directories exist and are writable by appuser
RUN mkdir -p /app/data/backups /app/data/reports && chown -R appuser:appuser /app

# Switch to non-root user for Hugging Face security
USER appuser

# Expose default Hugging Face Spaces port
EXPOSE 7860

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/webhooks/status || exit 1

# Start the application using dynamic $PORT (7860 on Hugging Face, or Render-assigned port)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
