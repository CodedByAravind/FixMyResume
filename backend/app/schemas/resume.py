import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

MONTH_YEAR_RE = re.compile(r"^\d{4}-\d{2}$")


def _validate_month_year(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    if not MONTH_YEAR_RE.match(value):
        raise ValueError("Date must be in YYYY-MM format")
    return value


def _validate_url(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    if not (value.startswith("http://") or value.startswith("https://")):
        raise ValueError("URL must start with http:// or https://")
    return value


class EducationBase(BaseModel):
    institution: str = Field(..., min_length=1, max_length=200)
    degree: Optional[str] = Field(None, max_length=200)
    field_of_study: Optional[str] = Field(None, max_length=200)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        return _validate_month_year(v)

    @model_validator(mode="after")
    def check_date_order(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: Optional[str] = Field(None, min_length=1, max_length=200)
    degree: Optional[str] = Field(None, max_length=200)
    field_of_study: Optional[str] = Field(None, max_length=200)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        return _validate_month_year(v)

    @model_validator(mode="after")
    def check_date_order(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class EducationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    position: int = 0


class ExperienceBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        return _validate_month_year(v)

    @model_validator(mode="after")
    def check_date_order(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        return _validate_month_year(v)

    @model_validator(mode="after")
    def check_date_order(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class ExperienceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    position: int = 0


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    url: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v: Optional[str]) -> Optional[str]:
        return _validate_url(v)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    url: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v: Optional[str]) -> Optional[str]:
        return _validate_url(v)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    position: int = 0


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str] = None
    position: int = 0


class CertificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    issuer: Optional[str] = Field(None, max_length=200)
    date_obtained: Optional[str] = None
    url: Optional[str] = None

    @field_validator("date_obtained")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        return _validate_month_year(v)

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v: Optional[str]) -> Optional[str]:
        return _validate_url(v)


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    issuer: Optional[str] = Field(None, max_length=200)
    date_obtained: Optional[str] = None
    url: Optional[str] = None

    @field_validator("date_obtained")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        return _validate_month_year(v)

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v: Optional[str]) -> Optional[str]:
        return _validate_url(v)


class CertificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    issuer: Optional[str] = None
    date_obtained: Optional[str] = None
    url: Optional[str] = None
    position: int = 0


class ResumeCreate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=5000)

    @field_validator("website", "linkedin", "github")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        return _validate_url(v)


class ResumeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=5000)

    @field_validator("website", "linkedin", "github")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        return _validate_url(v)


class ResumeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ResumeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    education: list[EducationOut] = []
    experience: list[ExperienceOut] = []
    projects: list[ProjectOut] = []
    skills: list[SkillOut] = []
    certifications: list[CertificationOut] = []
