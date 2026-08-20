from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.certification import Certification


def create_certification(db: Session, *, resume_id: int, position: int, **data) -> Certification:
    entry = Certification(resume_id=resume_id, position=position, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_certification_by_id(db: Session, entry_id: int, resume_id: int) -> Certification | None:
    return (
        db.query(Certification)
        .filter(Certification.id == entry_id, Certification.resume_id == resume_id)
        .first()
    )


def update_certification(db: Session, entry: Certification, **data) -> Certification:
    for key, value in data.items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_certification(db: Session, entry: Certification) -> None:
    db.delete(entry)
    db.commit()


def next_certification_position(db: Session, resume_id: int) -> int:
    max_pos = (
        db.query(func.max(Certification.position))
        .filter(Certification.resume_id == resume_id)
        .scalar()
    )
    return (max_pos if max_pos is not None else -1) + 1
