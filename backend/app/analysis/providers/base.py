from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from app.schemas.analysis import AnalysisResult


@dataclass
class SkillEntry:
    name: str
    category: Optional[str] = None


@dataclass
class ResumeContext:
    """Value object carrying the resume content the provider needs.

    Providers depend on this plain structure rather than SQLAlchemy models,
    keeping the analysis engine model-agnostic and easy to reuse/test.
    """
    title: str = ""
    full_name: str = ""
    summary: str = ""
    skills: list[SkillEntry] = field(default_factory=list)          # structured skills
    experience_titles: list[str] = field(default_factory=list)
    experience_descriptions: list[str] = field(default_factory=list)
    project_names: list[str] = field(default_factory=list)
    project_descriptions: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)              # institution/degree/field
    certifications: list[str] = field(default_factory=list)         # certification/issuer names

    def all_text(self) -> str:
        """Concatenate all resume text fields for keyword-based similarity."""
        parts = [
            self.title,
            self.full_name,
            self.summary,
            *[s.name for s in self.skills],
            *self.experience_titles,
            *self.experience_descriptions,
            *self.project_names,
            *self.project_descriptions,
            *self.education,
            *self.certifications,
        ]
        return "\n".join(p for p in parts if p)


class AnalysisProvider(ABC):
    """Interface for analyzing a resume against a job description.

    Implementations (e.g. RuleBasedAnalysisProvider now, an Ollama-based
    provider later) must return the same stable AnalysisResult contract so
    the API layer, AnalysisService and frontend are provider-agnostic.
    """
    name: str = "base"

    @abstractmethod
    def analyze(self, resume_context: ResumeContext, job_description: str) -> AnalysisResult:
        """Return a deterministic AnalysisResult for the given inputs."""
        raise NotImplementedError
