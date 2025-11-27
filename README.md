# fastapi-template

FastAPI template. Using FastAPI, SQLModel, PostgreSQL, Docker, GitHub Actions, automatic HTTPS and more.

## Usage

### `.env`

```ini
# .env

APP_NAME="FastAPI App"
APP_VERSION="v1.0.0"
APP_DESCRIPTION="FastAPI app description."
DEBUG=true
```

### Run

#### Development

```bash
uv run -m app.app
```

#### Production

```bash
uv run uvicorn --host 0.0.0.0 --port 8000 \
    --proxy-headers \
    --forwarded-allow-ips "*" \
    --workers 1 \
    --limit-concurrency 1024 \
    --limit-max-requests 10000 \
    --backlog 4096 \
    --log-level info \
    --timeout-keep-alive 5 \
    --no-use-colors \
    --no-server-header \
    app.app:app \
    --log-config app/uvicorn_logging.json
```

## References

- [**`FastAPI`**](https://fastapi.tiangolo.com/)
- [*`Pydantic`*: Data Validation and Settings Management (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/data/pydantic)
- [**`uvicorn`**: *ASGI* Server (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/web/uvicorn)
- [*`Swagger`*: *OpenAPI*](https://swagger.io/)
- [*`Starlette`*: *ASGI* Web part](https://www.starlette.io/)
- [Awesome List for FastAPI](https://github.com/mjhea0/awesome-fastapi)
