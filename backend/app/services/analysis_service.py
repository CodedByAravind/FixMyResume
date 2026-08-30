from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.analysis.providers.base import AnalysisProvider, ResumeContext, SkillEntry
from app.models.user import User
from app.repositories import analysis_repository
from app.schemas.analysis import AnalysisResult


def analyze_resume(
    db: Session,
    *,
    user: User,
    resume_id: int,
    job_description: str,
    provider: AnalysisProvider,
) -> AnalysisResult:
    """Load the user-owned resume and run the configured provider.

    Ownership is enforced via the repository query (resume must belong to
    the authenticated user); any other resume yields a 404. The service
    depends on the AnalysisProvider interface, not a concrete implementation.
    """
    resume = analysis_repository.get_owned_resume_with_sections(db, resume_id, user.id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    context = _build_resume_context(resume)
    return provider.analyze(context, job_description)


def analyze_context(
    provider: AnalysisProvider,
    context: ResumeContext,
    job_description: str,
) -> AnalysisResult:
    """"Run a provider on an already-built ResumeContext.

    Used by tailoring to re-score tailored content without duplicating the
    analysis engine or the provider lookup. Same AnalysisResult contract.
    """
    return provider.analyze(context, job_description)


def _build_resume_context(resume) -> ResumeContext:
    return ResumeContext(
        title=resume.title or "",
        full_name=resume.full_name or "",
        summary=resume.summary or "",
        skills=[SkillEntry(name=s.name, category=s.category) for s in resume.skills],
        experience_titles=[e.title for e in resume.experience if e.title],
        experience_descriptions=[e.description for e in resume.experience if e.description],
        project_names=[p.name for p in resume.projects if p.name],
        project_descriptions=[p.description for p in resume.projects if p.description],
        education=[
            " ".join(v for v in (e.institution, e.degree, e.field_of_study) if v)
            for e in resume.education
        ],
        certifications=[
            " ".join(v for v in (c.name, c.issuer) if v)
            for c in resume.certifications
        ],
    )
