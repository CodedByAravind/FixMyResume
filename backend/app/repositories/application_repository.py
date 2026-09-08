from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.models.application import JobApplication


def _owned_query(db: Session, user_id: int):
    return db.query(JobApplication).filter(JobApplication.user_id == user_id)


def get_owned_application(db: Session, *, application_id: int, user_id: int) -> Optional[JobApplication]:
    return (
        _owned_query(db, user_id)
        .options(selectinload(JobApplication.resume), selectinload(JobApplication.resume_version))
        .filter(JobApplication.id == application_id)
        .first()
    )


def list_owned_applications(
    db: Session,
    *,
    user_id: int,
    status: Optional[str] = None,
    q: Optional[str] = None,
    sort_by: str = "application_date",
    order: str = "desc",
):
    query = _owned_query(db, user_id)
    if status:
        query = query.filter(JobApplication.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            JobApplication.company.ilike(like)
            | JobApplication.job_title.ilike(like)
            | JobApplication.location.ilike(like)
        )
    sort_col = {
        "application_date": JobApplication.application_date,
        "created_at": JobApplication.created_at,
        "updated_at": JobApplication.updated_at,
        "company": JobApplication.company,
    }[sort_by]
    if order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    return query.all()


def create_application(
    db: Session,
    *,
    user_id: int,
    resume_id: int,
    resume_version_id: Optional[int],
    company: str,
    job_title: str,
    job_url: Optional[str],
    location: Optional[str],
    status: str,
    application_date: datetime,
    interview_date: Optional[datetime],
    notes: Optional[str],
) -> JobApplication:
    app = JobApplication(
        user_id=user_id,
        resume_id=resume_id,
        resume_version_id=resume_version_id,
        company=company,
        job_title=job_title,
        job_url=job_url,
        location=location,
        status=status,
        application_date=application_date,
        interview_date=interview_date,
        notes=notes,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def update_application(db: Session, application: JobApplication, **data) -> JobApplication:
    for key, value in data.items():
        setattr(application, key, value)
    db.commit()
    db.refresh(application)
    return application


def delete_application(db: Session, application: JobApplication) -> None:
    db.delete(application)
    db.commit()


def count_for_resume(db, resume_id):
    return db.query(JobApplication).filter(JobApplication.resume_id == resume_id).count()


def clear_version_references(db, version_id):
    apps = db.query(JobApplication).filter(JobApplication.resume_version_id == version_id).all()
    for app in apps:
        app.resume_version_id = None
    if apps:
        db.commit()
