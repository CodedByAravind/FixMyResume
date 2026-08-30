from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class ResumeVersion(Base):
    """A tailored version of a resume.

    Each version owns two immutable snapshot sets (source + tailored) so it
    stays reproducible even if the live resume is edited later.
    """
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False, default="Tailored Resume")
    job_description = Column(Text, nullable=False)
    analysis_score = Column(Integer, nullable=True)
    tailored_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    source_profile = relationship("VersionSourceProfile", back_populates="version", uselist=False, cascade="all, delete-orphan")
    source_education = relationship("VersionSourceEducation", back_populates="version", cascade="all, delete-orphan", order_by="VersionSourceEducation.position")
    source_experience = relationship("VersionSourceExperience", back_populates="version", cascade="all, delete-orphan", order_by="VersionSourceExperience.position")
    source_projects = relationship("VersionSourceProject", back_populates="version", cascade="all, delete-orphan", order_by="VersionSourceProject.position")
    source_skills = relationship("VersionSourceSkill", back_populates="version", cascade="all, delete-orphan", order_by="VersionSourceSkill.position")
    source_certifications = relationship("VersionSourceCertification", back_populates="version", cascade="all, delete-orphan", order_by="VersionSourceCertification.position")

    tailored_profile = relationship("VersionTailoredProfile", back_populates="version", uselist=False, cascade="all, delete-orphan")
    tailored_education = relationship("VersionTailoredEducation", back_populates="version", cascade="all, delete-orphan", order_by="VersionTailoredEducation.position")
    tailored_experience = relationship("VersionTailoredExperience", back_populates="version", cascade="all, delete-orphan", order_by="VersionTailoredExperience.position")
    tailored_projects = relationship("VersionTailoredProject", back_populates="version", cascade="all, delete-orphan", order_by="VersionTailoredProject.position")
    tailored_skills = relationship("VersionTailoredSkill", back_populates="version", cascade="all, delete-orphan", order_by="VersionTailoredSkill.position")
    tailored_certifications = relationship("VersionTailoredCertification", back_populates="version", cascade="all, delete-orphan", order_by="VersionTailoredCertification.position")
