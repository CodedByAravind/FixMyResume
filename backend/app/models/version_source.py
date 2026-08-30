from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class VersionSourceProfile(Base):
    __tablename__ = "version_source_profiles"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    full_name = Column(String(100), nullable=True)
    email = Column(String(254), nullable=True)
    phone = Column(String(30), nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(2048), nullable=True)
    linkedin = Column(String(2048), nullable=True)
    github = Column(String(2048), nullable=True)
    summary = Column(Text, nullable=True)
    version = relationship("ResumeVersion", back_populates="source_profile")


class _SourceSectionBase:
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)


class VersionSourceEducation(_SourceSectionBase, Base):
    __tablename__ = "version_source_education"
    institution = Column(String(200), nullable=False)
    degree = Column(String(200), nullable=True)
    field_of_study = Column(String(200), nullable=True)
    start_date = Column(String(7), nullable=True)
    end_date = Column(String(7), nullable=True)
    description = Column(Text, nullable=True)
    version = relationship("ResumeVersion", back_populates="source_education")


class VersionSourceExperience(_SourceSectionBase, Base):
    __tablename__ = "version_source_experience"
    company = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    location = Column(String(100), nullable=True)
    start_date = Column(String(7), nullable=True)
    end_date = Column(String(7), nullable=True)
    description = Column(Text, nullable=True)
    version = relationship("ResumeVersion", back_populates="source_experience")


class VersionSourceProject(_SourceSectionBase, Base):
    __tablename__ = "version_source_projects"
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(2048), nullable=True)
    version = relationship("ResumeVersion", back_populates="source_projects")


class VersionSourceSkill(_SourceSectionBase, Base):
    __tablename__ = "version_source_skills"
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    version = relationship("ResumeVersion", back_populates="source_skills")


class VersionSourceCertification(_SourceSectionBase, Base):
    __tablename__ = "version_source_certifications"
    name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=True)
    date_obtained = Column(String(7), nullable=True)
    url = Column(String(2048), nullable=True)
    version = relationship("ResumeVersion", back_populates="source_certifications")
