from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.resume_version import ResumeVersion
from app.models.user import User
from app.repositories import (
    application_repository,
    resume_repository,
    resume_version_repository,
)


def _utcnow() -> datetime:
    return datetime.utcnow()


def _get_owned_resume(db: Session, user: User, resume_id: int) -> Resume:
    resume = resume_repository.get_resume_by_id_and_user(db, resume_id, user.id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return resume


def _validate_version(db: Session, user: User, resume: Resume, resume_version_id) -> Optional[int]:
    """Ensure version belongs to user AND to the selected resume. None allowed."""
    if resume_version_id is None:
        return None
    version = resume_version_repository.get_owned_version(
        db, version_id=resume_version_id, resume_id=resume.id, user_id=user.id
    )
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")
    return resume_version_id



def create_application(db: Session, *, user: User, payload) -> object:
    resume = _get_owned_resume(db, user, payload.resume_id)
    version_id = _validate_version(db, user, resume, payload.resume_version_id)
    application_date = payload.application_date or _utcnow()

    app = application_repository.create_application(
        db,
        user_id=user.id,
        resume_id=resume.id,
        resume_version_id=version_id,
        company=payload.company,
        job_title=payload.job_title,
        job_url=payload.job_url,
        location=payload.location,
        status=payload.status,
        application_date=application_date,
        interview_date=payload.interview_date,
        notes=payload.notes,
    )
    return application_repository.get_owned_application(db, application_id=app.id, user_id=user.id)


def list_applications(
    db: Session, *, user: User,
    status: str | None,
    q: str | None,
    sort_by: str,
    order: str,
):
    return application_repository.list_owned_applications(
        db, user_id=user.id, status=status, q=q, sort_by=sort_by, order=order
    )


def get_application(db: Session, *, user: User, application_id: int) -> object:
    application = application_repository.get_owned_application(
        db, application_id=application_id, user_id=user.id
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    return application


def update_application(db: Session, *, user: User, application_id: int, payload) -> object:
    application = get_application(db, user=user, application_id=application_id)

    data = payload.model_dump(exclude_unset=True)

    # Re-validate resume/version ownership whenever they change.
    if "resume_id" in data:
        resume = _get_owned_resume(db, user, data["resume_id"])
        data["resume_id"] = resume.id
        # If version provided, must belong to new resume.
        version_id = data.get("resume_version_id")
        new_version = _validate_version(db, user, resume, version_id)
        data["resume_version_id"] = new_version
    elif "resume_version_id" in data:
        # Keep existing resume_id reference.
        app = application
        current_resume_id = app.resume_id
        resume = _get_owned_resume(db, user, current_resume_id)
        data["resume_version_id"] = _validate_version(db, user, resume, data["resume_version_id"])

    # Status/interview_date combination validation (server-side safety).
    new_status = data.get("status", application.status)
    new_interview = data.get("interview_date", application.interview_date)
    if (
        "status" in data or "interview_date" in data
    ) and new_interview is not None and new_status != "interview":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="interview_date is only valid when status is 'interview'.",
        )

    return application_repository.update_application(db, application, **data)


def delete_application(db: Session, *, user: User, application_id: int) -> None:
    application = get_application(db, user=user, application_id=application_id)
    application_repository.delete_application(db, application)
