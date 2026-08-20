from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class ExperienceEntry(Base):
    __tablename__ = "experience_entries"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    location = Column(String(100), nullable=True)
    start_date = Column(String(7), nullable=True)
    end_date = Column(String(7), nullable=True)
    description = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    resume = relationship("Resume", back_populates="experience")
