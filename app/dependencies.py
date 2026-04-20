"""Dependencies."""

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Request
from redis.asyncio import ConnectionPool as RedisConnectionPool
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, Any]:
    """Get Database session."""
    db_client: AsyncEngine = request.state.db_client
    async with AsyncSession(db_client) as session:
        yield session


async def get_redis_session(request: Request) -> AsyncGenerator[Redis, Any]:
    """Get Redis session."""
    redis_connection_pool: RedisConnectionPool = request.state.redis_connection_pool
    async with Redis(connection_pool=redis_connection_pool) as session:
        yield session
