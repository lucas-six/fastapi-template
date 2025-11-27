"""FastAPI App."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[Any, Any]:
    yield


app: FastAPI = FastAPI(
    title=settings.app_name,
    docs_url=settings.app_doc_url,
    debug=settings.debug,
    openapi_url=f'{settings.app_doc_url}/openapi.json',
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get('/api')
async def root() -> dict[str, str | bool]:
    return {'Hello': 'World', 'debug': settings.debug}


# Only for develop environment
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='app.app:app', host='', reload=True)
