"""Celery Worker."""

import logging
import os
from enum import StrEnum
from io import BytesIO
from typing import Any, TypedDict

import boto3
import httpx
import resend
from boto3.s3.transfer import TransferConfig as S3TransferConfig
from botocore.config import Config as S3Config
from celery import Celery
from redis import Redis
from sqlmodel import Session as SQLSession
from sqlmodel import create_engine
from types_boto3_s3.client import S3Client

from app.db_models import EmailAttachment, EmailWebhookEnum, EmailWebhookEventTypeEnum
from app.settings import get_settings

settings = get_settings()

logger = logging.getLogger('celery')

resend.api_key = settings.resend_api_key.get_secret_value()

client_name = f'{settings.app_name}-celery-{os.getpid()}'.replace(' ', '-')
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

redis_client = Redis.from_url(
    settings.redis_url.encoded_string(),
    encoding='utf-8',
    decode_responses=True,
    max_connections=settings.cache_max_conns,
    socket_connect_timeout=settings.cache_conn_timeout,
    socket_timeout=settings.cache_timeout,
    client_name=client_name,
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


class HandleResendEmailReceivedStatusEnum(StrEnum):
    """Handle Resend Email Received Status Enum."""

    SUCCESS = 'success'
    FAILED = 'failed'
    PROCESSING = 'processing'


class HandleResendEmailReceivedResult(TypedDict):
    status: HandleResendEmailReceivedStatusEnum
    save_to_s3: bool
    s3_keys: dict[str, str]


@celery_app.task(ignore_result=True)
def heartbeat() -> None:
    logger.debug('heartbeat')


@celery_app.task
def do_something() -> None:
    logger.debug('do_something')


@celery_app.task
def handle_resend_email_received(email_data: dict[str, Any]) -> HandleResendEmailReceivedResult:
    """Handle Resend email received event."""
    # Check if the message is already processed
    message_id = email_data['data']['message_id']
    message_lock_key = f'{settings.cache_prefix}:webhook:resend:message:{message_id}'
    if redis_client.exists(message_lock_key):
        return {
            'status': HandleResendEmailReceivedStatusEnum.PROCESSING,
            'save_to_s3': False,
            's3_keys': {},
        }
    redis_client.set(message_lock_key, '1', ex=settings.resend_webhook_lock_expire)

    email_id = email_data['data']['email_id']
    logger.debug(f'Processing email [{email_id}]: {email_data}')

    # Save attachment to S3
    s3_client: S3Client | None = None
    bucket_name = settings.resend_attachments_s3_bucket
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
                config=S3Config(
                    signature_version=settings.resend_attachments_s3_signature_version,
                    s3={'addressing_style': settings.resend_attachments_s3_addressing_style},  # pyright: ignore[reportArgumentType]
                    connect_timeout=settings.resend_attachments_s3_conn_timeout,
                ),
            )
        else:
            s3_client = boto3_session.client(
                's3',
                region_name=settings.resend_attachments_s3_region,
                config=S3Config(
                    connect_timeout=settings.resend_attachments_s3_conn_timeout,
                ),
            )

    attachment_list = email_data['data']['attachments']
    s3_keys: dict[str, str] = {}
    download_timeout_config = httpx.Timeout(settings.resend_webhook_attachments_download_timeout)
    with (
        httpx.Client(timeout=download_timeout_config) as http_client,
        SQLSession(sql_db_engine) as sql_session,
    ):
        for attachment in attachment_list:
            attachment_id = attachment['id']
            content_type = attachment['content_type']

            # Save attachment to S3
            if s3_client:
                file_ext = content_type.split('/')[-1]

                attachment_detail = resend.Emails.Receiving.Attachments.get(email_id, attachment_id)
                attachment_response = http_client.get(attachment_detail['download_url'])
                bucket_key = '/'.join(
                    [
                        settings.resend_attachments_s3_prefix,
                        f'resend_{email_id}_{attachment_id}.{file_ext}',
                    ]
                )
                s3_client.upload_fileobj(
                    BytesIO(attachment_response.content),
                    bucket_name,
                    bucket_key,
                    Config=S3TransferConfig(
                        multipart_threshold=settings.resend_attachments_s3_multipart_threshold
                    ),
                )

                sql_session.add(
                    EmailAttachment(
                        webhook=EmailWebhookEnum.RESEND,
                        webhook_event_type=EmailWebhookEventTypeEnum.EMAIL_RECEIVED,
                        message_id=message_id,
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
                        s3_bucket=bucket_name,
                        s3_key=bucket_key,
                    )
                )

                if settings.resend_attachments_s3_presigned_expire > 0:
                    s3_keys[bucket_key] = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': bucket_key},
                        ExpiresIn=settings.resend_attachments_s3_presigned_expire,
                    )

        sql_session.commit()

    return {
        'status': HandleResendEmailReceivedStatusEnum.SUCCESS,
        'save_to_s3': s3_client is not None,
        's3_keys': s3_keys,
    }
