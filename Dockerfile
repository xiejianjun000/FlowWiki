# FlowWiki Docker Image
# Multi-stage build for minimal production image

FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.13-slim-bookworm

LABEL org.opencontainers.image.title="FlowWiki"
LABEL org.opencontainers.image.description="AI-human compound knowledge base methodology"
LABEL org.opencontainers.image.url="https://github.com/xiejianjun000/FlowWiki"
LABEL org.opencontainers.image.source="https://github.com/xiejianjun000/FlowWiki"

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Ensure scripts in PATH
ENV PATH=/root/.local/bin:$PATH

# Copy FlowWiki files
COPY --chown=1000:1000 . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash flowwiki \
    && chown -R flowwiki:flowwiki /app

USER flowwiki

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import sys; from pathlib import Path; sys.exit(0 if Path('wiki/index.md').exists() or Path('SCHEMA.md').exists() else 1)"

# Default: run lint check
CMD ["python", "_scripts/lint.py"]
