"""Celery Worker."""

import logging
from typing import Any

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


@celery_app.task
def process_email_received(email_data: dict[str, Any]) -> None:
    email_id = email_data['data']['email_id']
    logger.debug(f'Processing email [{email_id}]: {email_data}')
    attachment_list = email_data['data']['attachments']
    for attachment in attachment_list:
        attachment_info = {
            'id': attachment['id'],
            'filename': attachment['filename'],
            'content_type': attachment['content_type'],
            'content_disposition': attachment['content_disposition'],
            'content_id': attachment['content_id'],
        }
        logger.debug(f'Attachment info: {attachment_info}')
