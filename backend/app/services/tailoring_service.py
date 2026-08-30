from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.analysis.providers.base import AnalysisProvider, ResumeContext, SkillEntry
from app.models.resume import Resume
from app.models.resume_version import ResumeVersion
from app.models import version_source as src
from app.models import version_tailored as tai
from app.models.user import User
from app.repositories import (
    analysis_repository,
    resume_version_repository,
)
from app.schemas.resume import CertificationOut, EducationOut, ExperienceOut, ProjectOut, SkillOut
from app.schemas.tailoring import (
    CompareOut,
    TailoredVersionOut,
    VersionDetailOut,
    VersionProfileOut,
    VersionSnapshotOut,
    VersionSummaryOut,
)
from app.services import analysis_service
from app.tailoring.providers.base import TailoringContext, TailoringProvider


# ---------- small helpers ----------

def _default_version_name() -> str:
    return "Tailored Resume"


def _version_name() -> str:
    return "Tailored Resume"


def _to_snapshot_out(profile, education, experience, projects, skills, certifications) -> VersionSnapshotOut:
    p = VersionProfileOut(
        title=profile.title, full_name=profile.full_name, email=profile.email,
        phone=profile.phone, location=profile.location, website=profile.website,
        linkedin=profile.linkedin, github=profile.github, summary=profile.summary,
    ) if profile is not None else VersionProfileOut(summary=None)
    return VersionSnapshotOut(
        profile=p,
        education=[EducationOut.model_validate(e) for e in (education or [])],
        experience=[ExperienceOut.model_validate(e) for e in (experience or [])],
        projects=[ProjectOut.model_validate(e) for e in (projects or [])],
        skills=[SkillOut.model_validate(e) for e in (skills or [])],
        certifications=[CertificationOut.model_validate(e) for e in (certifications or [])],
    )


def _get_owned_resume(db: Session, user: User, resume_id: int) -> Resume:
    resume = analysis_repository.get_owned_resume_with_sections(db, resume_id, user.id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return resume


def _get_owned_version(db: Session, user: User, resume_id: int, version_id: int) -> ResumeVersion:
    version = resume_version_repository.get_owned_version(db, version_id=version_id, resume_id=resume_id, user_id=user.id)
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found.")
    return version


def _tailored_resume_context(result) -> ResumeContext:
    return ResumeContext(
        summary=result.summary or "",
        skills=[SkillEntry(name=s["name"], category=s.get("category")) for s in result.skills],
        experience_titles=[e.get("title") or "" for e in result.experience],
        experience_descriptions=[e.get("description") or "" for e in result.experience],
        project_names=[p.get("name") or "" for p in result.projects],
        project_descriptions=[p.get("description") or "" for p in result.projects],
    )


def _strip(row: dict) -> dict:
    return {k: v for k, v in row.items() if k not in ("id", "version_id", "resume_id", "position", "created_at", "updated_at")}


def _snapshot_rows(version: ResumeVersion) -> dict:
    return {
        "source": _snapshot_out(
            version.source_profile, version.source_education, version.source_experience,
            version.source_projects, version.source_skills, version.source_certifications,
        ),
        "tailored": _snapshot_out(
            version.tailored_profile, version.tailored_education, version.tailored_experience,
            version.tailored_projects, version.tailored_skills, version.tailored_certifications,
        ),
    }


def _snapshot_out(profile, education, experience, projects, skills, certifications) -> VersionSnapshotOut:
    return _to_snapshot_out(profile, education, experience, projects, skills, certifications)


# ---------- public service ----------

def tailor_resume(
    db: Session,
    *,
    user: User,
    resume_id: int,
    payload,
    tailoring_provider: TailoringProvider,
    analysis_provider: AnalysisProvider,
) -> TailoredVersionOut:
    resume = _get_owned_resume(db, user, resume_id)

    # 1) Reuse Phase 3 analysis against the live resume (no duplication).
    source_analysis = analysis_service.analyze_resume(
        db, user=user, resume_id=resume_id,
        job_description=payload.job_description, provider=analysis_provider,
    )

    # 2) Run tailoring provider on a rich context; re-score tailored snapshot.
    ctx = _tailoring_context_from_resume(resume)
    result = tailoring_provider.tailor(ctx, source_analysis, payload.job_description)
    tailored_ctx = _tailored_resume_context(result)
    tailored_analysis = analysis_service.analyze_context(analysis_provider, tailored_ctx, payload.job_description)

    # 3) Persist version + two immutable snapshots.
    version = resume_version_repository.create_version(
        db, resume_id=resume_id, user_id=user.id,
        name=payload.name or _version_name(),
        job_description=payload.job_description,
        analysis_score=source_analysis.score,
        tailored_score=tailored_analysis.score,
    )

    version.source_profile = src.VersionSourceProfile(
        title=resume.title, full_name=resume.full_name, email=resume.email,
        phone=resume.phone, location=resume.location, website=resume.website,
        linkedin=resume.linkedin, github=resume.github, summary=resume.summary,
    )
    version.source_skills = [src.VersionSourceSkill(**_strip(s), position=i) for i, s in enumerate(_source_skills(resume))]
    version.source_experience = [src.VersionSourceExperience(**_strip(e), position=i) for i, e in enumerate(_source_exp(resume))]
    version.source_projects = [src.VersionSourceProject(**_strip(p), position=i) for i, p in enumerate(_source_projs(resume))]
    version.source_education = [src.VersionSourceEducation(**_strip(e), position=i) for i, e in enumerate(_source_edu(resume))]
    version.source_certifications = [src.VersionSourceCertification(**_strip(c), position=i) for i, c in enumerate(_source_certs(resume))]

    version.tailored_profile = tai.VersionTailoredProfile(
        title=resume.title, full_name=resume.full_name, email=resume.email,
        phone=resume.phone, location=resume.location, website=resume.website,
        linkedin=resume.linkedin, github=resume.github, summary=result.summary,
    )
    version.tailored_skills = [tai.VersionTailoredSkill(**{k: v for k, v in _strip(s).items() if k in ("name", "category")}, position=i) for i, s in enumerate(result.skills)]
    version.tailored_experience = [tai.VersionTailoredExperience(**{k: v for k, v in _strip(e).items() if k in ("company", "title", "location", "start_date", "end_date", "description")}, position=i) for i, e in enumerate(result.experience)]
    version.tailored_projects = [tai.VersionTailoredProject(**{k: v for k, v in _strip(p).items() if k in ("name", "description", "url")}, position=i) for i, p in enumerate(result.projects)]
    version.tailored_education = [tai.VersionTailoredEducation(**{k: v for k, v in _strip(e).items() if k in ("institution", "degree", "field_of_study", "start_date", "end_date", "description")}, position=i) for i, e in enumerate(result.education)]
    version.tailored_certifications = [tai.VersionTailoredCertification(**{k: v for k, v in _strip(c).items() if k in ("name", "issuer", "date_obtained", "url")}, position=i) for i, c in enumerate(result.certifications)]

    db.add(version)
    db.commit()
    version = _get_owned_version(db, user, resume_id, version.id)
    return _to_tailored_out(version, result, tailored_analysis)


def list_versions(db: Session, user: User, resume_id: int) -> list[VersionSummaryOut]:
    _get_owned_resume(db, user, resume_id)
    versions = resume_version_repository.list_versions_by_resume(db, resume_id=resume_id, user_id=user.id)
    return [VersionSummaryOut.model_validate(v) for v in versions]


def get_version(db: Session, user: User, resume_id: int, version_id: int) -> VersionDetailOut:
    _get_owned_resume(db, user, resume_id)
    version = _get_owned_version(db, user, resume_id, version_id)
    snaps = _snapshot_rows(version)
    return VersionDetailOut(
        id=version.id, resume_id=version.resume_id, name=version.name,
        analysis_score=version.analysis_score, tailored_score=version.tailored_score,
        created_at=_iso(version.created_at),
        source=snaps["source"], tailored=snaps["tailored"],
    )


def compare_version(db: Session, user: User, resume_id: int, version_id: int) -> CompareOut:
    version = get_version(db, user, resume_id, version_id)
    return CompareOut(
        resume_id=resume_id, version_id=version.id, version_name=version.name,
        analysis_score=version.analysis_score, tailored_score=version.tailored_score,
        changed_sections=_diff_sections(version.source, version.tailored),
        source=version.source, tailored=version.tailored,
    )


def delete_version(db: Session, user: User, resume_id: int, version_id: int) -> None:
    resume_version_repository.delete_version(db, _get_owned_version(db, user, resume_id, version_id))


# ---------- internal ----------

def _tailoring_context_from_resume(resume: Resume) -> TailoringContext:
    return TailoringContext(
        title=resume.title or "", full_name=resume.full_name or "", summary=resume.summary or "",
        skills=_source_skills(resume), experience=_source_exp(resume),
        projects=_source_projs(resume), education=_source_edu(resume), certifications=_source_certs(resume),
    )


def _source_skills(resume):
    return [{"name": s.name, "category": s.category} for s in resume.skills]

def _source_exp(resume):
    return [{"company": e.company, "title": e.title, "location": e.location, "start_date": e.start_date, "end_date": e.end_date, "description": e.description} for e in resume.experience]

def _source_projs(resume):
    return [{"name": p.name, "description": p.description, "url": p.url} for p in resume.projects]

def _source_edu(resume):
    return [{"institution": e.institution, "degree": e.degree, "field_of_study": e.field_of_study, "start_date": e.start_date, "end_date": e.end_date, "description": e.description} for e in resume.education]

def _source_certs(resume):
    return [{"name": c.name, "issuer": c.issuer, "date_obtained": c.date_obtained, "url": c.url} for c in resume.certifications]


def _strip(row: dict) -> dict:
    return {k: v for k, v in row.items() if k not in ("id", "version_id", "resume_id", "position", "created_at", "updated_at")}


def _iso(dt) -> str:
    return dt.isoformat() if dt else ""


def _to_tailored_out(version: ResumeVersion, result, tailored_analysis) -> TailoredVersionOut:
    snaps = _snapshot_rows(version)
    return TailoredVersionOut(
        id=version.id, resume_id=version.resume_id, name=version.name,
        analysis_score=version.analysis_score, tailored_score=version.tailored_score, created_at=_iso(version.created_at),
        source=snaps["source"], tailored=snaps["tailored"],
        changed_sections=result.changed_sections,
        recommendations=result.recommendations, warnings=result.warnings,
    )


def _diff_sections(source: VersionSnapshotOut, tailored: VersionSnapshotOut) -> list[str]:
    changed: list[str] = []
    if source.profile and tailored.profile and source.profile.summary != tailored.profile.summary:
        changed.append("summary")
    if [s.name for s in source.skills] != [s.name for s in tailored.skills]:
        changed.append("skills")
    if [(e.company, e.title) for e in source.experience] != [(e.company, e.title) for e in tailored.experience]:
        changed.append("experience")
    if [p.name for p in source.projects] != [p.name for p in tailored.projects]:
        changed.append("projects")
    if [e.institution for e in source.education] != [e.institution for e in tailored.education]:
        changed.append("education")
    if [c.name for c in source.certifications] != [c.name for c in tailored.certifications]:
        changed.append("certifications")
    return changed
