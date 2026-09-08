import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="RESTRICT"), nullable=False, index=True)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True, index=True)

    company = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    job_url = Column(String(2048), nullable=True)
    location = Column(String(100), nullable=True)
    status = Column(String(30), nullable=False, default="applied")
    application_date = Column(DateTime, nullable=False)
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    resume_version = relationship("ResumeVersion", back_populates="applications")
