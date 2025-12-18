"""Dependencies."""

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import HTTPException, Request
from redis.asyncio import ConnectionPool as RedisConnectionPool
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_sql_db_session(request: Request) -> AsyncGenerator[AsyncSession, Any]:
    """Get SQL Database session."""
    sql_db_client: AsyncEngine | None = request.state.sql_db_client
    if sql_db_client:
        async with AsyncSession(sql_db_client) as session:
            yield session
    else:
        raise HTTPException(status_code=500, detail='SQL Database connection not found')


async def get_redis_session(request: Request) -> AsyncGenerator[Redis, Any]:
    """Get Redis session."""
    redis_connection_pool: RedisConnectionPool = request.state.redis_connection_pool
    async with Redis(connection_pool=redis_connection_pool) as session:
        yield session
