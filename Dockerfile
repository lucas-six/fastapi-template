# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --locked --no-dev


# Then, use a final image without uv
FROM python:3.13-slim-bookworm

# Copy the application from the builder
COPY --from=builder /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV UVICORN_PORT=8000
ENV UVICORN_WORKERS=1
ENV UVICORN_CONCURRENCY=1024
ENV UVICORN_MAX_REQUESTS=10000
ENV UVICORN_BACKLOG=4096
ENV UVICORN_LOG_LEVEL=info
ENV UVICORN_TIMEOUT_KEEP_ALIVE=5
WORKDIR /app

# Run the application.
CMD ["sh", "-c", "uvicorn app.app:app \
    --host 0.0.0.0 \
    --port ${UVICORN_PORT} \
    --proxy-headers \
    --forwarded-allow-ips \"*\" \
    --workers ${UVICORN_WORKERS} \
    --limit-concurrency ${UVICORN_CONCURRENCY} \
    --limit-max-requests ${UVICORN_MAX_REQUESTS} \
    --backlog ${UVICORN_BACKLOG} \
    --log-level ${UVICORN_LOG_LEVEL} \
    --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE} \
    --no-use-colors \
    --no-server-header \
    --log-config app/uvicorn_logging.json"]
