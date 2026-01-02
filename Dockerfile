# Alpha-PM Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/
COPY alembic.ini ./
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd -m -u 1000 alphapm && chown -R alphapm:alphapm /app
USER alphapm

# Health check endpoint
EXPOSE 8080

# Run the application
CMD ["uv", "run", "python", "-m", "src.main"]
