from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.project import ProjectEntry


def create_project(db: Session, *, resume_id: int, position: int, **data) -> ProjectEntry:
    entry = ProjectEntry(resume_id=resume_id, position=position, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_project_by_id(db: Session, entry_id: int, resume_id: int) -> ProjectEntry | None:
    return (
        db.query(ProjectEntry)
        .filter(ProjectEntry.id == entry_id, ProjectEntry.resume_id == resume_id)
        .first()
    )


def update_project(db: Session, entry: ProjectEntry, **data) -> ProjectEntry:
    for key, value in data.items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_project(db: Session, entry: ProjectEntry) -> None:
    db.delete(entry)
    db.commit()


def next_project_position(db: Session, resume_id: int) -> int:
    max_pos = (
        db.query(func.max(ProjectEntry.position))
        .filter(ProjectEntry.resume_id == resume_id)
        .scalar()
    )
    return (max_pos if max_pos is not None else -1) + 1
