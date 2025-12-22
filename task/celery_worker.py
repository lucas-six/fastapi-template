"""Celery Worker."""

import logging
import os
from io import BytesIO
from typing import Any

import boto3
import httpx
import resend
from botocore.config import Config
from celery import Celery
from sqlmodel import Session as SQLSession
from sqlmodel import create_engine

from app.db_models import EmailAttachment, EmailWebhookEnum, EmailWebhookEventTypeEnum
from app.settings import get_settings

settings = get_settings()

logger = logging.getLogger('celery')

resend.api_key = settings.resend_api_key.get_secret_value()

client_name = f'{settings.app_name}-celery-[{os.getpid()}]'
sql_db_engine = create_engine(
    settings.sql_db_url.encoded_string(),
    pool_size=settings.sql_db_pool_size,
    max_overflow=20,
    pool_timeout=settings.sql_db_pool_timeout,
    connect_args={
        'application_name': client_name,
        'connect_timeout': settings.sql_db_connect_timeout,
    },
    logging_name=client_name,
    echo=False,
)


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
def resend_process_email_received(email_data: dict[str, Any]) -> None:
    email_id = email_data['data']['email_id']
    logger.debug(f'Processing email [{email_id}]: {email_data}')

    # Save attachment to S3
    s3_client: boto3.client | None = None
    if settings.resend_attachments_s3_access_key_id:
        boto3_session = boto3.Session(
            aws_access_key_id=settings.resend_attachments_s3_access_key_id,
            aws_secret_access_key=settings.resend_attachments_s3_access_secret.get_secret_value(),
            region_name=settings.resend_attachments_s3_region,
        )
        if settings.resend_attachments_s3_endpoint_url:
            s3_client = boto3_session.client(
                's3',
                endpoint_url=settings.resend_attachments_s3_endpoint_url.encoded_string(),
                config=Config(
                    signature_version=settings.resend_attachments_s3_signature_version,
                    s3={'addressing_style': settings.resend_attachments_s3_addressing_style},
                ),
            )
        else:
            s3_client = boto3_session.client(
                's3',
                region_name=settings.resend_attachments_s3_region,
            )

    attachment_list = email_data['data']['attachments']
    with httpx.Client() as http_client, SQLSession(sql_db_engine) as sql_session:
        for attachment in attachment_list:
            attachment_id = attachment['id']
            content_type = attachment['content_type']

            # Save attachment to S3
            if s3_client:
                file_ext = content_type.split('/')[-1]

                attachment_detail = resend.Emails.Receiving.Attachments.get(email_id, attachment_id)
                attachment_response = http_client.get(attachment_detail['download_url'])
                s3_client.upload_fileobj(
                    BytesIO(attachment_response.content),
                    settings.resend_attachments_s3_bucket,
                    '/'.join(
                        [
                            settings.resend_attachments_s3_prefix,
                            f'resend_{email_id}_{attachment_id}.{file_ext}',
                        ]
                    ),
                )

                sql_session.add(
                    EmailAttachment(
                        webhook=EmailWebhookEnum.RESEND,
                        webhook_event_type=EmailWebhookEventTypeEnum.EMAIL_RECEIVED,
                        message_id=email_data['data']['message_id'],
                        email_id=email_id,
                        attachment_id=attachment_id,
                        email_subject=email_data['data']['subject'],
                        email_from=email_data['data']['from'],
                        email_to=email_data['data']['to'],
                        filename=attachment['filename'],
                        content_type=content_type,
                        file_size=attachment_detail['size'],
                        created_at=email_data['data']['created_at'],
                        s3_region=settings.resend_attachments_s3_region,
                        s3_bucket=settings.resend_attachments_s3_bucket,
                        s3_key=f'{settings.resend_attachments_s3_prefix}/{email_id}/{attachment_id}.{file_ext}',
                    )
                )
        sql_session.commit()
