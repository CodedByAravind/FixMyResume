from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, default="Untitled Resume")
    full_name = Column(String(100), nullable=True)
    email = Column(String(254), nullable=True)
    phone = Column(String(30), nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(2048), nullable=True)
    linkedin = Column(String(2048), nullable=True)
    github = Column(String(2048), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="resumes")
    education = relationship("EducationEntry", back_populates="resume", cascade="all, delete-orphan", order_by="EducationEntry.position")
    experience = relationship("ExperienceEntry", back_populates="resume", cascade="all, delete-orphan", order_by="ExperienceEntry.position")
    projects = relationship("ProjectEntry", back_populates="resume", cascade="all, delete-orphan", order_by="ProjectEntry.position")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan", order_by="Skill.position")
    certifications = relationship("Certification", back_populates="resume", cascade="all, delete-orphan", order_by="Certification.position")
    applications = relationship("JobApplication", back_populates="resume")
