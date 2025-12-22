"""Database Models."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import EmailStr, StrictBool, field_serializer, field_validator
from sqlmodel import JSON, Column, Field, SQLModel

from app.settings import get_settings

settings = get_settings()


class EmailWebhookEnum(StrEnum):
    """Email Webhook Enum."""

    RESEND = 'resend'


class EmailWebhookEventTypeEnum(StrEnum):
    """Email Webhook Event Type Enum."""

    EMAIL_RECEIVED = 'email.received'


class S3TypeEnum(StrEnum):
    """S3 Type Enum."""

    AMAZON_S3 = 'amazon_s3'
    ALIYUN_OSS = 'aliyun_oss'


class BasicModel(SQLModel):
    """Basic Model."""

    id: int | None = Field(default=None, primary_key=True)
    is_active: StrictBool = True
    created_time: datetime
    updated_time: datetime
    remark: str = Field(max_length=512, default='')
    extra: dict[str, Any] | None = Field(default=None, sa_type=JSON)

    @field_validator('updated_time')
    @classmethod
    def auto_update_time(cls, value: datetime) -> datetime:
        return value if value else datetime.now()

    @field_serializer('created_time')
    def serialize_created_time(self, value: datetime) -> str:
        return value.strftime(settings.datetime_format)

    @field_serializer('updated_time')
    def serialize_updated_time(self, value: datetime) -> str:
        return value.strftime(settings.datetime_format)


class TemplateDemo(BasicModel, table=True):
    """Template Demo Model."""

    __tablename__ = 'template_demo'  # pyright: ignore[reportAssignmentType]

    name: str = Field(max_length=255)


class EmailAttachment(SQLModel, table=True):
    """Email Attachment Model."""

    __tablename__ = 'email_attachment'  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    webhook: EmailWebhookEnum = EmailWebhookEnum.RESEND
    webhook_event_type: EmailWebhookEventTypeEnum = EmailWebhookEventTypeEnum.EMAIL_RECEIVED
    message_id: str = Field(max_length=64)
    email_id: str = Field(max_length=64)
    attachment_id: str = Field(max_length=64)
    email_subject: str = Field(max_length=256)
    email_from: EmailStr
    email_to: list[EmailStr] = Field(sa_column=Column(JSON))
    filename: str = Field(max_length=256)
    content_type: str = Field(max_length=256)
    file_size: int = Field(default=0, ge=0)
    created_at: datetime
    s3_type: S3TypeEnum = S3TypeEnum.AMAZON_S3
    s3_region: str = Field(max_length=64)
    s3_bucket: str = Field(max_length=64)
    s3_key: str = Field(max_length=256)

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        unique_together = [('webhook', 'email_id', 'attachment_id')]

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        return value.strftime(settings.datetime_format)
