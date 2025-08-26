#FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:bookworm-slim AS builder
FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.12
#RUN apt-get update
#RUN apt-get install -y --no-install-recommends gcc
#WORKDIR /app
#RUN --mount=type=cache,target=/root/.cache/uv \
#    --mount=type=bind,source=uv.lock,target=uv.lock \
#    --mount=type=bind,source=pyproject.toml,target=pyproject.toml
COPY . /app
WORKDIR /app
#RUN --mount=type=cache,target=/root/.cache/uv \
#    uv sync --frozen --no-dev --no-editable
#FROM --platform=linux/amd64 gcr.io/distroless/cc
FROM  iplayabc-docker.pkg.coding.net/huaweicloud/ireadabc/distroless_cc:250825.2
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv



# Then, use a final image without uv
#FROM --platform=linux/amd64 gcr.io/distroless/cc
#
## Copy the Python version
#COPY --from=builder --chown=python:python /python /python
#
#WORKDIR /app
#RUN uv sync
## Copy the application from the builder
#COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
RUN ls /usr/local/bin
RUN ls
RUN uv sync
# Run the FastAPI application by default
#CMD ["fastapi", "run", "--host", "0.0.0.0", "/app/.venv/lib/python3.12/site-packages/uv_docker_example"]
CMD ["python", "app.py"]