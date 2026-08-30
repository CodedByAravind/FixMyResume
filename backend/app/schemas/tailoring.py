from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.resume import (
    CertificationOut,
    EducationOut,
    ExperienceOut,
    ProjectOut,
    SkillOut,
)
from app.schemas.analysis import SkillMatch


class TailorRequest(BaseModel):
    job_description: str = Field(..., min_length=1, max_length=20000)
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class VersionProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None


class VersionSnapshotOut(BaseModel):
    profile: VersionProfileOut
    education: list[EducationOut] = []
    experience: list[ExperienceOut] = []
    projects: list[ProjectOut] = []
    skills: list[SkillOut] = []
    certifications: list[CertificationOut] = []


class TailoredVersionOut(BaseModel):
    id: int
    resume_id: int
    name: str
    analysis_score: Optional[int] = None
    tailored_score: Optional[int] = None
    created_at: datetime
    source: VersionSnapshotOut
    tailored: VersionSnapshotOut
    changed_sections: list[str] = []
    recommendations: list[str] = []
    warnings: list[str] = []


class VersionSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    name: str
    analysis_score: Optional[int] = None
    tailored_score: Optional[int] = None
    created_at: datetime


class VersionDetailOut(BaseModel):
    id: int
    resume_id: int
    name: str
    analysis_score: Optional[int] = None
    tailored_score: Optional[int] = None
    created_at: datetime
    source: VersionSnapshotOut
    tailored: VersionSnapshotOut


class CompareOut(BaseModel):
    resume_id: int
    version_id: int
    version_name: str
    analysis_score: Optional[int] = None
    tailored_score: Optional[int] = None
    changed_sections: list[str]
    source: VersionSnapshotOut
    tailored: VersionSnapshotOut
    recommendations: list[str] = []
    warnings: list[str] = []
