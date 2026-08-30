from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.models.resume_version import ResumeVersion

_VERSION_OPTS = [
    selectinload(ResumeVersion.source_profile),
    selectinload(ResumeVersion.source_education),
    selectinload(ResumeVersion.source_experience),
    selectinload(ResumeVersion.source_projects),
    selectinload(ResumeVersion.source_skills),
    selectinload(ResumeVersion.source_certifications),
    selectinload(ResumeVersion.tailored_profile),
    selectinload(ResumeVersion.tailored_education),
    selectinload(ResumeVersion.tailored_experience),
    selectinload(ResumeVersion.tailored_projects),
    selectinload(ResumeVersion.tailored_skills),
    selectinload(ResumeVersion.tailored_certifications),
]


def get_owned_version(
    db: Session,
    *,
    version_id: int,
    resume_id: int,
    user_id: int,
) -> Optional[ResumeVersion]:
    return (
        db.query(ResumeVersion)
        .options(*_VERSION_OPTS)
        .filter(
            ResumeVersion.id == version_id,
            ResumeVersion.resume_id == resume_id,
            ResumeVersion.user_id == user_id,
        )
        .first()
    )


def list_versions_by_resume(
    db: Session,
    *,
    resume_id: int,
    user_id: int,
) -> list[ResumeVersion]:
    return (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume_id, ResumeVersion.user_id == user_id)
        .order_by(ResumeVersion.created_at.desc())
        .all()
    )


def create_version(db: Session, *, resume_id: int, user_id: int, name: str, job_description: str, analysis_score: Optional[int], tailored_score: Optional[int] = None) -> ResumeVersion:
    version = ResumeVersion(
        resume_id=resume_id,
        user_id=user_id,
        name=name,
        job_description=job_description,
        analysis_score=analysis_score,
        tailored_score=tailored_score,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def delete_version(db: Session, version: ResumeVersion) -> None:
    db.delete(version)
    db.commit()
