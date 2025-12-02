"""FastAPI App."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastapi import FastAPI, Request
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
    sql_db_client: AsyncEngine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[dict[str, Any]]:
    """Application lifespan handler"""
    # Startup
    pid = await pid_str()
    logger.info(f'Starting {_app.title} [{pid}]...')

    if settings.sql_db_enabled:
        sql_db_client = create_async_engine(
            settings.sql_db_url.get_secret_value(),
            pool_size=settings.sql_db_pool_size,
            max_overflow=20,
            pool_timeout=settings.sql_db_pool_timeout,
            connect_args={
                'application_name': f'{_app.title} [{pid}]',
                'connect_timeout': settings.sql_db_connect_timeout,
            },
            logging_name=_app.title,
            echo=False,
        )
    else:
        sql_db_client = None

    yield {'sql_db_client': sql_db_client}

    # Shutdown
    if settings.sql_db_enabled and sql_db_client:
        await sql_db_client.dispose()
        logger.debug(f'Disposing SQL Database connection [{pid}]...')
    logger.info(f'Shutting down {_app.title} [{pid}]...')


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
async def root(request: Request) -> dict[str, str | bool]:
    logger.debug(f'Root endpoint [{await pid_str()}]...')
    sql_db_client = request.state.sql_db_client
    if settings.sql_db_enabled and sql_db_client:
        async with AsyncSession(sql_db_client) as session:
            message = await session.exec(select(func.count(col(TemplateDemo.id))))
        logger.debug(f'SQL Database message: {message.first()}')
    return {'Hello': 'World', 'debug': settings.debug}


# Only for develop environment
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='app.app:app', host='', reload=True)
