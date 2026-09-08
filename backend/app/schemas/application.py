from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

APPLICATION_STATUSES = {"applied", "interview", "offer", "rejected", "withdrawn"}
SORT_FIELDS = {"application_date", "created_at", "updated_at", "company"}
ORDER_VALUES = {"asc", "desc"}


def _valid_url(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    if not (value.startswith("http://") or value.startswith("https://")):
        raise ValueError("URL must start with http:// or https://")
    return value


class ApplicationCreate(BaseModel):
    resume_id: int = Field(...)
    resume_version_id: Optional[int] = None
    company: str = Field(..., min_length=1, max_length=200)
    job_title: str = Field(..., min_length=1, max_length=200)
    job_url: Optional[str] = Field(None, max_length=2048)
    location: Optional[str] = Field(None, max_length=100)
    status: str = "applied"
    application_date: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("job_url")
    @classmethod
    def validate_job_url(cls, v):
        return _valid_url(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in APPLICATION_STATUSES:
            raise ValueError("Invalid status")
        return v

    @field_validator("interview_date")
    @classmethod
    def validate_interview(cls, v, info):
        status = info.data.get("status")
        if v is not None and status != "interview":
            raise ValueError("interview_date is only valid when status is 'interview'")
        return v


class ApplicationUpdate(BaseModel):
    resume_id: Optional[int] = None
    resume_version_id: Optional[int] = None
    company: Optional[str] = Field(None, min_length=1, max_length=200)
    job_title: Optional[str] = Field(None, min_length=1, max_length=200)
    job_url: Optional[str] = Field(None, max_length=2048)
    location: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    application_date: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("job_url")
    @classmethod
    def validate_job_url(cls, v):
        return _valid_url(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in APPLICATION_STATUSES:
            raise ValueError("Invalid status")
        return v


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resume_id: int
    resume_version_id: Optional[int] = None
    company: str
    job_title: str
    job_url: Optional[str] = None
    location: Optional[str] = None
    status: str
    application_date: datetime
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApplicationListOut(BaseModel):
    """Lightweight fields for the list view, with resume/version summaries."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    resume_version_id: Optional[int] = None
    company: str
    job_title: str
    status: str
    application_date: datetime
    interview_date: Optional[datetime] = None
    updated_at: datetime
