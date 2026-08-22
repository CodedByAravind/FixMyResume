from typing import Optional

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    job_description: str = Field(..., min_length=1, max_length=20000)


class SkillMatch(BaseModel):
    name: str
    category: Optional[str] = None


class ScoreDetails(BaseModel):
    skill_score: float
    keyword_score: float
    role_domain_score: float
    overall: int


class AnalysisResult(BaseModel):
    """Stable provider-agnostic contract consumed by the frontend.

    Every provider (rule-based now, LLM/Ollama later) must return this shape.
    """
    score: int
    score_details: ScoreDetails
    matched_skills: list[SkillMatch]
    missing_skills: list[SkillMatch]
    job_keywords: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendations: list[str]
    summary: str
    provider: str
