"""Settings."""

from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')

    # Datetime format
    datetime_format: str = '%Y-%m-%d %H:%M:%S'

    app_name: str
    app_version: str = '0.1.0'
    app_root_url: str = '/'
    app_description: str = ''
    debug: bool = False

    # Database (PostgreSQL)
    sql_db_enabled: bool = False
    sql_db_url: PostgresDsn = PostgresDsn(
        'postgresql+psycopg://postgres:postgres@localhost:5432/postgres'
    )
    sql_db_connect_timeout: float = 5.0
    sql_db_pool_size: int = 10
    sql_db_pool_timeout: float = 5.0

    # Cache (Redis)
    redis_url: RedisDsn = RedisDsn('redis://:foobared@localhost:6379/0')
    cache_max_conns: int = 4096
    cache_conn_timeout: float | None = 3.0
    cache_timeout: float | None = 3.5
    cache_prefix: str = ''


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
