"""Dependencies."""

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import HTTPException, Request
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
