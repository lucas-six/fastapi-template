"""Database Models."""

from datetime import datetime
from typing import Any

from pydantic import StrictBool, field_serializer, field_validator
from sqlmodel import JSON, Field, SQLModel

from app.settings import get_settings

settings = get_settings()


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
