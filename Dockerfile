FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ src/
COPY addon/ addon/
COPY skills/ skills/
COPY mcp_adapter.py .
COPY start_server.py .

# Expose MCP server port
EXPOSE 9876

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('localhost', 9876)); s.close()" || exit 1

# Run MCP server
CMD ["python", "mcp_adapter.py"]
