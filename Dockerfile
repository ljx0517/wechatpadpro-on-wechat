# Builder Stage
FROM python:3.12-slim-bookworm AS builder

# Install build dependencies including gcc
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from its official image
COPY --from=ghcr.io/astral-sh/uv:bookworm-slim /uv /bin/uv

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copy project files and lockfile
COPY pyproject.toml uv.lock /app/

# Install dependencies with uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY . /app

# Production Stage
FROM python:3.12-slim-bookworm AS production

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Set up the PATH to include the virtual environment's binaries
ENV PATH="/app/.venv/bin:$PATH"

# Expose port and define the command to run your application
#EXPOSE 8000
#CMD ["uvicorn", "your_app_module:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "app.py"]