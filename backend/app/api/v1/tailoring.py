from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.analysis import get_provider as get_analysis_provider
from app.api.v1.deps import get_current_active_user
from app.core.config import settings
from app.database.db import get_db
from app.models.user import User
from app.schemas.tailoring import (
    CompareOut,
    TailoredVersionOut,
    TailorRequest,
    VersionDetailOut,
    VersionSummaryOut,
)
from app.services import tailoring_service
from app.tailoring.providers.base import TailoringProvider
from app.tailoring.providers.rule_based import RuleBasedTailoringProvider

router = APIRouter(tags=["tailoring"])

_TAILORING_PROVIDERS = {
    "rule_based": RuleBasedTailoringProvider,
}


def get_tailoring_provider() -> TailoringProvider:
    cls = _TAILORING_PROVIDERS.get(settings.TAILORING_PROVIDER, RuleBasedTailoringProvider)
    return cls()


@router.post(
    "/resumes/{resume_id}/tailor",
    response_model=TailoredVersionOut,
    status_code=status.HTTP_201_CREATED,
)
def tailor_resume(
    resume_id: int,
    payload: TailorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tailoring_provider: TailoringProvider = Depends(get_tailoring_provider),
    analysis_provider=Depends(get_analysis_provider),
):
    return tailoring_service.tailor_resume(
        db,
        user=current_user,
        resume_id=resume_id,
        payload=payload,
        tailoring_provider=tailoring_provider,
        analysis_provider=analysis_provider,
    )


@router.get("/resumes/{resume_id}/versions", response_model=list[VersionSummaryOut])
def list_versions(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return tailoring_service.list_versions(db, current_user, resume_id)


@router.get("/resumes/{resume_id}/versions/{version_id}", response_model=VersionDetailOut)
def get_version(
    resume_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return tailoring_service.get_version(db, current_user, resume_id, version_id)


@router.get("/resumes/{resume_id}/versions/{version_id}/compare", response_model=CompareOut)
def compare_version(
    resume_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return tailoring_service.compare_version(db, current_user, resume_id, version_id)


@router.delete("/resumes/{resume_id}/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_version(
    resume_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    tailoring_service.delete_version(db, current_user, resume_id, version_id)
