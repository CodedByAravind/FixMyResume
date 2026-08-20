from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.user import User
from app.repositories import resume_repository


def _get_owned_resume_or_404(db: Session, resume_id: int, user_id: int) -> Resume:
    resume = resume_repository.get_resume_by_id_and_user(db, resume_id, user_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return resume


def create_resume(db: Session, user: User, payload) -> Resume:
    personal_info = payload.model_dump(exclude={"title"}, exclude_none=True)
    return resume_repository.create_resume(
        db,
        user_id=user.id,
        title=payload.title or "Untitled Resume",
        **personal_info,
    )


def list_resumes(db: Session, user: User) -> list[Resume]:
    return resume_repository.list_resumes_by_user(db, user.id)


def get_resume(db: Session, user: User, resume_id: int) -> Resume:
    return _get_owned_resume_or_404(db, resume_id, user.id)


def update_resume(db: Session, user: User, resume_id: int, payload) -> Resume:
    resume = _get_owned_resume_or_404(db, resume_id, user.id)
    data = payload.model_dump(exclude_unset=True)
    return resume_repository.update_resume(db, resume, **data)


def delete_resume(db: Session, user: User, resume_id: int) -> None:
    resume = _get_owned_resume_or_404(db, resume_id, user.id)
    resume_repository.delete_resume(db, resume)
