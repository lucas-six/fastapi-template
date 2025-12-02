"""FastAPI App."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastapi import FastAPI, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db_models import TemplateDemo
from app.settings import get_settings
from app.utils import pid_str

settings = get_settings()

# Logger
logger = logging.getLogger(f'uvicorn.{settings.app_name}')
if settings.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


class State(TypedDict):
    sql_db_client: AsyncEngine | None
    redis_client: Redis | None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[dict[str, Any]]:
    """Application lifespan handler"""
    # Startup
    _pid_str = await pid_str()
    _pid = os.getpid()
    client_name = f'{_app.title} [{_pid}]'
    client_name_str = f'{_app.title} [{_pid_str}]'
    logger.info(f'Starting {client_name_str}...')

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
    else:
        sql_db_client = None

    redis_client_name = client_name.replace(' ', '-')
    redis_client_name_str = f'{_app.title} [{_pid_str}]'.replace(' ', '-')
    logger.debug(f'Redis client name: {redis_client_name}')
    async with Redis.from_url(
        url=settings.redis_url.encoded_string(),
        encoding='utf-8',
        decode_responses=True,
        max_connections=settings.cache_max_conns,
        socket_connect_timeout=settings.cache_conn_timeout,
        socket_timeout=settings.cache_timeout,
        client_name=redis_client_name,
    ) as redis_client:
        yield {'sql_db_client': sql_db_client, 'redis_client': redis_client}

        # Shutdown
        if settings.sql_db_enabled and sql_db_client:
            await sql_db_client.dispose()
            logger.debug(f'SQL Database connection {client_name_str} disposing...')

    logger.debug(f'Redis client {redis_client_name_str} disconnected')
    logger.info(f'Shutting down {client_name_str}...')


app: FastAPI = FastAPI(
    title=settings.app_name,
    docs_url=f'{settings.app_root_url}/docs',
    debug=settings.debug,
    openapi_url=f'{settings.app_root_url}/docs/openapi.json',
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get(f'{settings.app_root_url}')
async def root(request: Request) -> dict[str, str | bool | None]:
    logger.debug(f'Root endpoint [{await pid_str()}]...')

    # SQL Database
    sql_db_client = request.state.sql_db_client
    if settings.sql_db_enabled and sql_db_client:
        async with AsyncSession(sql_db_client) as session:
            message = await session.exec(select(func.count(col(TemplateDemo.id))))
        logger.debug(f'SQL Database message: {message.first()}')

    # Cache (Redis)
    cache_val = await request.state.redis_client.get(f'{settings.cache_prefix}')

    return {'Hello': 'World', 'debug': settings.debug, 'cache_val': cache_val}


# Only for develop environment
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='app.app:app', host='', reload=True)
