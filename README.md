# fastapi-template

FastAPI template. Using FastAPI, SQLModel, PostgreSQL, Docker, GitHub Actions, automatic HTTPS and more.

## Usage

### `.env`

```ini
# .env

APP_NAME="FastAPI App"
APP_VERSION="v1"
APP_ROOT_URL="/api"
APP_DESCRIPTION="FastAPI app description."
DEBUG=true

SQL_DB_ENABLED=true
SQL_DB_URL="postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
SQL_DB_CONNECT_TIMEOUT=5.0
SQL_DB_POOL_SIZE=10
SQL_DB_POOL_TIMEOUT=5.0
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
- [SQL Database (PostgreSQL): `SQLModel` + `Alembic` (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/system_services/sql_db)
- [*`Swagger`*: *OpenAPI*](https://swagger.io/)
- [*`Starlette`*: *ASGI* Web part](https://www.starlette.io/)
- [Awesome List for FastAPI](https://github.com/mjhea0/awesome-fastapi)
