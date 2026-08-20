from sqlalchemy.orm import Session

from app.models.resume import Resume


def create_resume(db: Session, *, user_id: int, title: str = "Untitled Resume", **personal_info) -> Resume:
    resume = Resume(user_id=user_id, title=title, **personal_info)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes_by_user(db: Session, user_id: int) -> list[Resume]:
    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.updated_at.desc())
        .all()
    )


def get_resume_by_id_and_user(db: Session, resume_id: int, user_id: int) -> Resume | None:
    return (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == user_id)
        .first()
    )


def update_resume(db: Session, resume: Resume, **data) -> Resume:
    for key, value in data.items():
        setattr(resume, key, value)
    db.commit()
    db.refresh(resume)
    return resume


def delete_resume(db: Session, resume: Resume) -> None:
    db.delete(resume)
    db.commit()
