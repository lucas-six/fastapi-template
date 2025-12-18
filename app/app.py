"""FastAPI App."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, Request
from redis.asyncio import ConnectionPool as RedisConnectionPool
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db_models import TemplateDemo
from app.dependencies import get_redis_session, get_sql_db_session
from app.settings import get_settings
from app.utils import pid_str
from app.webhook import api as webhook_api
from task.celery_worker import do_something

settings = get_settings()

# Logger
logger = logging.getLogger(f'uvicorn.{settings.app_name}')
if settings.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


class State(TypedDict):
    sql_db_client: AsyncEngine | None
    redis_connection_pool: RedisConnectionPool


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[dict[str, Any]]:
    """Application lifespan handler"""
    # Startup
    _pid_str = await pid_str()
    _pid = os.getpid()
    client_name = f'{_app.title} [{_pid}]'.replace(' ', '-')
    client_name_str = f'{_app.title} [{_pid_str}]'.replace(' ', '-')
    logger.info(f'Starting {client_name_str}...')

    sql_db_client = None
    if settings.sql_db_enabled:
        sql_db_client = create_async_engine(
            settings.sql_db_url.encoded_string(),
            pool_size=settings.sql_db_pool_size,
            max_overflow=20,
            pool_timeout=settings.sql_db_pool_timeout,
            connect_args={
                'application_name': client_name,
                'connect_timeout': settings.sql_db_connect_timeout,
            },
            logging_name=_app.title,
            echo=False,
        )

    redis_connection_pool: RedisConnectionPool = RedisConnectionPool.from_url(
        url=settings.redis_url.encoded_string(),
        encoding='utf-8',
        decode_responses=True,
        max_connections=settings.cache_max_conns,
        socket_connect_timeout=settings.cache_conn_timeout,
        socket_timeout=settings.cache_timeout,
        client_name=client_name,
    )

    yield {
        'sql_db_client': sql_db_client,
        'redis_connection_pool': redis_connection_pool,
    }

    # Shutdown
    if settings.sql_db_enabled and sql_db_client:
        await sql_db_client.dispose()
        logger.debug(f'SQL Database connection {client_name_str} disposing...')
    await redis_connection_pool.disconnect()
    logger.debug(f'Redis connection pool {client_name_str} disconnected')

    logger.info(f'Shutting down {client_name_str}...')


app: FastAPI = FastAPI(
    title=settings.app_name,
    docs_url=f'{settings.app_root_url}/docs',
    redoc_url=f'{settings.app_root_url}/redoc',
    debug=settings.debug,
    openapi_url=f'{settings.app_root_url}/docs/openapi.json',
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)


# Routers
app.include_router(
    webhook_api.router,
    prefix=f'{settings.app_root_url}/webhook',
    tags=['Webhook', 'Resend'],
)


@app.get(f'{settings.app_root_url}')
async def root(
    request: Request,
    sql_db_session: AsyncSession = Depends(get_sql_db_session),
    redis_session: Redis = Depends(get_redis_session),
) -> dict[str, str | bool | None]:
    logger.debug(f'Root endpoint [{await pid_str()}]...')

    # SQL Database
    message = await sql_db_session.exec(select(func.count(col(TemplateDemo.id))))
    logger.debug(f'SQL Database message: {message.first()}')

    # Cache (Redis)
    cache_val = await redis_session.get(f'{settings.cache_prefix}')

    # Task (Celery: RabbitMQ/Redis)
    task = do_something.delay()
    logger.debug(f'do_something task {task.id} delayed')

    return {'Hello': 'World', 'debug': settings.debug, 'cache_val': cache_val}


@app.get(f'{settings.app_root_url}/status/{{task_id}}')
async def status(task_id: str, request: Request) -> dict[str, str | bool | None]:
    task = AsyncResult(task_id)
    if task.ready():
        return {'status': 'DONE', 'result': task.get()}
    else:
        return {'status': 'IN_PROGRESS'}


# Only for develop environment
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='app.app:app', reload=True)
