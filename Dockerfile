# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --locked --no-cache

# Run the application.
CMD ["uv", "run", "uvicorn", "app.app:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--proxy-headers", \
    "--forwarded-allow-ips", "*", \
    "--workers", "1", \
    "--limit-concurrency", "1024", \
    "--limit-max-requests", "10000", \
    "--backlog", "4096", \
    "--log-level", "info", \
    "--timeout-keep-alive", "5", \
    "--no-use-colors", \
    "--no-server-header", \
    "--log-config", "app/uvicorn_logging.json"]
