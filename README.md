# fastapi-template

FastAPI template.
Using FastAPI, SQLModel, PostgreSQL, Redis, RabbitMQ, Docker, GitHub Actions, automatic HTTPS and more.

## Features

- Virtual Environment support: `uv`
- SQL Database support: `PostgreSQL`
- Caching support: `Redis`
- Message Queue support: `RabbitMQ`
- Containerization support: `Docker`
- GitHub Actions support: `GitHub Actions`
- Automatic HTTPS support: `Automatic HTTPS`

## System Requirements

- Python 3.13
- PostgreSQL 16
- Redis 8.4
- Docker Engine 29.1
- GitHub Actions
- Automatic HTTPS

## Usage

### `.env`

```ini
# .env

APP_NAME=FastAPI App
APP_VERSION=v1
APP_ROOT_URL=/api
APP_DESCRIPTION=FastAPI App description.
DEBUG=true

# SQL Database (PostgreSQL)
SQL_DB_ENABLED=true
SQL_DB_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres
SQL_DB_CONNECT_TIMEOUT=5.0
SQL_DB_POOL_SIZE=10
SQL_DB_POOL_TIMEOUT=5.0

# Cache (Redis)
REDIS_URL=redis://:foobared@localhost:6379/0
CACHE_PREFIX=
CACHE_MAX_CONNS=4096
CACHE_CONN_TIMEOUT=3.0
CACHE_TIMEOUT=3.5
```

### Run

#### Development

```bash
uv run -m app.app
```

```bash
docker build -t fastapi-template:<tag> .  # <tag> is the tag of the image
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

```basg
docker run -d --network=host --env-file .env fastapi-template:<tag>

docker logs -f <container_id>
docker stop <container_id>
docker rm <container_id>
docker ps -a
```

## References

- [**`FastAPI`**](https://fastapi.tiangolo.com/)
- [*`Pydantic`*: Data Validation and Settings Management (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/data/pydantic)
- [**`uvicorn`**: *ASGI* Server (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/web/uvicorn)
- [SQL Database (PostgreSQL): `SQLModel` + `Alembic` (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/system_services/sql_db)
- [Cache (Redis): **`redis-py`** (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/system_services/redis)
- [*`Swagger`*: *OpenAPI*](https://swagger.io/)
- [*`Starlette`*: *ASGI* Web part](https://www.starlette.io/)
- [Awesome List for FastAPI](https://github.com/mjhea0/awesome-fastapi)
