# fastapi-template

FastAPI template.
Using FastAPI, SQLModel, PostgreSQL, Redis, Celery, RabbitMQ, Docker,
GitHub Actions, S3 compatible storage, AI APIs and more.

## Features

- Virtual Environment support: `uv`
- Database support: `PostgreSQL`
- Caching support: `Redis`
- Task Queue support: `Celery`
- Message Queue support: `RabbitMQ`
- Containerization support: `Docker`
- Workflow support: `GitHub Actions`
- Email integration: `Resend`
- S3 compatible storage support: `Amazon S3` or `Aliyun OSS`
- AI support: `Qwen`

## System Requirements

- Python 3.13+
- PostgreSQL 16+
- Redis 8+
- RabbitMQ 4.2+ (optional)
- S3 storage: `AWS S3`, `Aliyun OSS` (optional)
- Docker Engine 29.1+
- Integration
  - Email: `Resend`
  - AI: `OpenAI`, `Qwen`

## Usage

### `.env`

```ini
# .env

APP_NAME="FastAPI App"
APP_VERSION=v1
APP_ROOT_URL=/api
APP_DESCRIPTION="FastAPI App description."
DEBUG=true

# Database (PostgreSQL)
DB_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres
DB_CONNECT_TIMEOUT=5.0
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=5.0

# Cache (Redis)
REDIS_URL=redis://:foobared@localhost:6379/0
CACHE_MAX_CONNS=4096
CACHE_CONN_TIMEOUT=3.0
CACHE_TIMEOUT=3.5
CACHE_PREFIX=fastapi-template

# Task (Celery with RabbitMQ/Redis)
TASK_QUEUE_BROKER=amqp://guest:guest@localhost:5672
#TASK_QUEUE_BROKER=redis://:foobared@localhost:6379/0
TASK_QUEUE_BACKEND=redis://:foobared@localhost:6379/0
TASK_TIME_LIMIT=60
TASK_QUEUE_BROKER_CONNECTION_TIMEOUT=3.0
TASK_QUEUE_BROKER_CONNECTION_MAX_RETRIES=3
TASK_QUEUE_RESULT_EXPIRES=86400

# Resend
RESEND_API_KEY=
RESEND_WEBHOOK_SECRET=
RESEND_WEBHOOK_PUBLISH_TO_REDIS=false
#RESEND_WEBHOOK_QUEUE_MAXLEN=100
RESEND_WEBHOOK_LOCK_EXPIRE=10
RESEND_WEBHOOK_ATTACHMENTS_DOWNLOAD_TIMEOUT=10.0

# S3
S3_ACCESS_KEY_ID=
S3_ACCESS_SECRET=""
S3_REGION=""
S3_BUCKET="resend_attachments"
S3_ENDPOINT_URL=https://s3.oss-cn-hangzhou.aliyuncs.com
S3_CONN_TIMEOUT=4.5
S3_SIGNATURE_VERSION=s3
S3_ADDRESSING_STYLE=virtual
S3_KEY_PREFIX=""
S3_MULTIPART_THRESHOLD=1073741824
S3_PRESIGNED_EXPIRE=3600  # 0 for no presigned URL

# AI API
#AI_API_KEY=openai_api_key
#AI_API_BASE_URL=openai_api_base_url
#AI_API_MODEL=openai_api_model
#AI_API_MAX_RETRIES=2
#AI_API_UPLOAD_FILE_TIMEOUT=10.0

# uvicorn (for docker)
UVICORN_PORT=8000
UVICORN_WORKERS=1
UVICORN_CONCURRENCY=1024
UVICORN_MAX_REQUESTS=10000
UVICORN_BACKLOG=4096
UVICORN_LOG_LEVEL=info
UVICORN_TIMEOUT_KEEP_ALIVE=5
```

### Run

#### Development / Testing

```bash
# Run database migrations
uv run alembic check
uv run alembic upgrade head

uv run -m app.app
# uv run uvicorn --host 0.0.0.0 --port 8000 app.app:app
uv run --env-file .env celery -A task.celery_worker worker --loglevel=debug --concurrency=1
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
