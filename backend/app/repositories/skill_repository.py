from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.skill import Skill


def create_skill(db: Session, *, resume_id: int, position: int, **data) -> Skill:
    entry = Skill(resume_id=resume_id, position=position, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_skill_by_id(db: Session, entry_id: int, resume_id: int) -> Skill | None:
    return (
        db.query(Skill)
        .filter(Skill.id == entry_id, Skill.resume_id == resume_id)
        .first()
    )


def update_skill(db: Session, entry: Skill, **data) -> Skill:
    for key, value in data.items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_skill(db: Session, entry: Skill) -> None:
    db.delete(entry)
    db.commit()


def next_skill_position(db: Session, resume_id: int) -> int:
    max_pos = (
        db.query(func.max(Skill.position))
        .filter(Skill.resume_id == resume_id)
        .scalar()
    )
    return (max_pos if max_pos is not None else -1) + 1
