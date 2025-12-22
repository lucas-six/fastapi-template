"""Settings."""

from functools import lru_cache

from pydantic import AmqpDsn, HttpUrl, PostgresDsn, RedisDsn, SecretStr
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
    cache_prefix: str = 'fastapi-template'

    # Task (Celery)
    task_queue_broker: RedisDsn | AmqpDsn = AmqpDsn('amqp://guest:guest@localhost:5672')
    task_queue_backend: RedisDsn | None = None
    task_time_limit: int | None = None  # 任务执行时间限制（秒）
    task_timezone: str = 'UTC'
    task_queue_broker_connection_timeout: float = 3.0
    task_queue_broker_connection_max_retries: int = 3
    task_queue_result_expires: int = 60 * 60 * 24
    # task_queue_default_retry_delay: int = 60

    # Resend
    resend_api_key: SecretStr = SecretStr('')
    resend_webhook_secret: SecretStr = SecretStr('')
    resend_webhook_publish_to_redis: bool = False
    resend_webhook_queue_maxlen: int | None = 100  # Redis Streams max length
    resend_webhook_lock_expire: int = 10  # Webhook lock expire time
    resend_webhook_attachments_download_conn_timeout: float = 4.5
    resend_webhook_attachments_download_timeout: float = 10.0
    resend_attachments_s3_access_key_id: str | None = None
    resend_attachments_s3_access_secret: SecretStr = SecretStr('')
    resend_attachments_s3_region: str = ''
    resend_attachments_s3_endpoint_url: HttpUrl | None = None  # Aliyun OSS
    resend_attachments_s3_signature_version: str = 's3'
    resend_attachments_s3_addressing_style: str = 'virtual'
    resend_attachments_s3_bucket: str = 'resend-attachments'
    resend_attachments_s3_prefix: str = ''
    resend_attachments_s3_presigned_expire: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
