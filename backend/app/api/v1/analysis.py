from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analysis.providers.base import AnalysisProvider
from app.analysis.providers.rule_based import RuleBasedAnalysisProvider
from app.api.v1.deps import get_current_active_user
from app.core.config import settings
from app.database.db import get_db
from app.models.user import User
from app.schemas.analysis import AnalysisRequest, AnalysisResult
from app.services import analysis_service

router = APIRouter(tags=["analysis"])


# Provider selected from configuration; the API/service depend on the
# interface so a future OllamaAnalysisProvider can be swapped in via settings
# without changing the contract.
_PROVIDERS = {
    "rule_based": RuleBasedAnalysisProvider,
}


def get_provider() -> AnalysisProvider:
    provider_cls = _PROVIDERS.get(settings.ANALYSIS_PROVIDER, RuleBasedAnalysisProvider)
    return provider_cls()


@router.post("/resumes/{resume_id}/analyze", response_model=AnalysisResult)
def analyze_resume(
    resume_id: int,
    payload: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    provider: AnalysisProvider = Depends(get_provider),
):
    return analysis_service.analyze_resume(
        db,
        user=current_user,
        resume_id=resume_id,
        job_description=payload.job_description,
        provider=provider,
    )
