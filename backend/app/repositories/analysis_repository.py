from sqlalchemy.orm import Session, selectinload

from app.models.resume import Resume


def get_owned_resume_with_sections(db: Session, resume_id: int, user_id: int) -> Resume | None:
    """Load a user-owned resume together with all its sections.

    Uses selectinload to avoid N+1 lazy queries when the analysis engine
    reads every relationship. Ownership is enforced by the user_id filter.
    """
    return (
        db.query(Resume)
        .options(
            selectinload(Resume.skills),
            selectinload(Resume.experience),
            selectinload(Resume.projects),
            selectinload(Resume.education),
            selectinload(Resume.certifications),
        )
        .filter(Resume.id == resume_id, Resume.user_id == user_id)
        .first()
    )
