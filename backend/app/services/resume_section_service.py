from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import resume_repository


def _get_owned_resume_or_404(db: Session, resume_id: int, user_id: int):
    resume = resume_repository.get_resume_by_id_and_user(db, resume_id, user_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return resume


def _integrity_error_to_409(exc: IntegrityError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Duplicate entry (e.g., a skill with this name already exists).",
    )


def create_entry(db: Session, user: User, resume_id: int, *, create_fn, next_position_fn, data: dict):
    _get_owned_resume_or_404(db, resume_id, user.id)
    position = next_position_fn(db, resume_id)
    try:
        return create_fn(db, resume_id=resume_id, position=position, **data)
    except IntegrityError as exc:
        db.rollback()
        raise _integrity_error_to_409(exc) from exc


def update_entry(db: Session, user: User, resume_id: int, entry_id: int, *, get_fn, update_fn, data: dict):
    _get_owned_resume_or_404(db, resume_id, user.id)
    entry = get_fn(db, entry_id, resume_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found.",
        )
    try:
        return update_fn(db, entry, **data)
    except IntegrityError as exc:
        db.rollback()
        raise _integrity_error_to_409(exc) from exc


def delete_entry(db: Session, user: User, resume_id: int, entry_id: int, *, get_fn, delete_fn):
    _get_owned_resume_or_404(db, resume_id, user.id)
    entry = get_fn(db, entry_id, resume_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found.",
        )
    delete_fn(db, entry)
