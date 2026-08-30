from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from app.schemas.analysis import AnalysisResult


@dataclass
class TailoringContext:
    """Rich snapshot of the resume given to a tailoring provider.

    Unlike the analysis ResumeContext (which carries only text fields), this
    carries every section as ordered dicts so a provider can reorder, rewrite
    (using only existing information) and return full content for snapshotting.
    """
    title: str = ""
    full_name: str = ""
    summary: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    skills: list[dict[str, Any]] = field(default_factory=list)
    experience: list[dict[str, Any]] = field(default_factory=list)
    projects: list[dict[str, Any]] = field(default_factory=list)
    education: list[dict[str, Any]] = field(default_factory=list)
    certifications: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TailoringResult:
    """Stable provider-agnostic contract produced by a TailoringProvider.

    The provider returns complete section content (reordered/rewritten from
    existing information only) plus metadata. A future LLM-based provider
    must return the same shape without changing the service/API/frontend.
    """
    summary: Optional[str]
    skills: list[dict[str, Any]] = field(default_factory=list)
    experience: list[dict[str, Any]] = field(default_factory=list)
    projects: list[dict[str, Any]] = field(default_factory=list)
    education: list[dict[str, Any]] = field(default_factory=list)
    certifications: list[dict[str, Any]] = field(default_factory=list)
    changed_sections: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    provider: str = "base"


class TailoringProvider(ABC):
    """Interface for tailoring a resume against a job description.

    Implementations (RuleBasedTailoringProvider now, an Ollama-based provider
    later) must return the same stable TailoringResult contract.
    """
    name: str = "base"

    @abstractmethod
    def tailor(
        self,
        context: TailoringContext,
        analysis: AnalysisResult,
        job_description: str,
    ) -> TailoringResult:
        raise NotImplementedError
