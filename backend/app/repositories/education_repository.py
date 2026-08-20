from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.education import EducationEntry


def create_education(db: Session, *, resume_id: int, position: int, **data) -> EducationEntry:
    entry = EducationEntry(resume_id=resume_id, position=position, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_education_by_id(db: Session, entry_id: int, resume_id: int) -> EducationEntry | None:
    return (
        db.query(EducationEntry)
        .filter(EducationEntry.id == entry_id, EducationEntry.resume_id == resume_id)
        .first()
    )


def update_education(db: Session, entry: EducationEntry, **data) -> EducationEntry:
    for key, value in data.items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_education(db: Session, entry: EducationEntry) -> None:
    db.delete(entry)
    db.commit()


def next_education_position(db: Session, resume_id: int) -> int:
    max_pos = (
        db.query(func.max(EducationEntry.position))
        .filter(EducationEntry.resume_id == resume_id)
        .scalar()
    )
    return (max_pos if max_pos is not None else -1) + 1
