"""Celery Worker."""

import logging

from celery import Celery

from app.settings import get_settings

settings = get_settings()

logger = logging.getLogger('celery')


celery_app = Celery(
    settings.app_name,
    broker=settings.task_queue_broker.encoded_string(),
    backend=settings.task_queue_backend.encoded_string() if settings.task_queue_backend else None,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=settings.task_queue_broker_connection_max_retries,
    broker_connection_timeout=settings.task_queue_broker_connection_timeout,
)
celery_app.config_from_object('task.celeryconfig')


@celery_app.task(ignore_result=True)
def heartbeat() -> None:
    logger.debug('heartbeat')


@celery_app.task
def do_something() -> None:
    logger.debug('do_something')
