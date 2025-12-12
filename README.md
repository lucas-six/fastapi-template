# fastapi-template

FastAPI template.
Using FastAPI, SQLModel, PostgreSQL, Redis, Celery, RabbitMQ, Docker,
GitHub Actions, automatic HTTPS and more.

## Features

- Virtual Environment support: `uv`
- SQL Database support: `PostgreSQL`
- Caching support: `Redis`
- Task Queue support: `Celery`
- Message Queue support: `RabbitMQ`
- Containerization support: `Docker`
- GitHub Actions support: `GitHub Actions`
- Automatic HTTPS support: `Automatic HTTPS`

## System Requirements

- Python 3.13+
- PostgreSQL 16+
- Redis 8.4+
- RabbitMQ 4.2+
- Docker Engine 29.1+
- GitHub Actions
- Automatic HTTPS

## Usage

### `.env`

```ini
# .env

APP_NAME="FastAPI App"
APP_VERSION=v1
APP_ROOT_URL=/api
APP_DESCRIPTION="FastAPI App description."
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

# Task (Celery with RabbitMQ/Redis)
TASK_QUEUE_BROKER=amqp://guest:guest@localhost:5672
#TASK_QUEUE_BROKER=redis://:foobared@localhost:6379/0
TASK_QUEUE_BACKEND=redis://:foobared@localhost:6379/0
TASK_TIME_LIMIT=60
TASK_QUEUE_BROKER_CONNECTION_TIMEOUT=3.0
TASK_QUEUE_BROKER_CONNECTION_MAX_RETRIES=3
TASK_QUEUE_RESULT_EXPIRES=86400
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

uv run --env-file .env celery -A task.celery_worker worker --loglevel=info --concurrency=1
uv run --env-file .env celery -A task.celery_worker beat --loglevel=info
```

```bash
docker run -d --network=host --env-file .env fastapi-template:<tag>

docker logs -f <container_id>
docker stop <container_id>
docker rm <container_id>
docker ps -a

# Run App with Celery
docker compose up -d
```

## References

- [**`FastAPI`**](https://fastapi.tiangolo.com/)
- [*`Pydantic`*: Data Validation and Settings Management (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/data/pydantic)
- [**`uvicorn`**: *ASGI* Server (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/web/uvicorn)
- [SQL Database (PostgreSQL): `SQLModel` + `Alembic` (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/system_services/sql_db)
- [Cache (Redis): **`redis-py`** (Python Cookbook)](https://lucas-six.github.io/python-cookbook/cookbook/system_services/redis)
- [**`celery`**: Task Queue](https://docs.celeryq.dev/en/stable/)
- [Message Queue (RabbitMQ): **`pika`**](https://pika.readthedocs.io/en/stable/index.html)
- [*`Swagger`*: *OpenAPI*](https://swagger.io/)
- [*`Starlette`*: *ASGI* Web part](https://www.starlette.io/)
- [Awesome List for FastAPI](https://github.com/mjhea0/awesome-fastapi)
