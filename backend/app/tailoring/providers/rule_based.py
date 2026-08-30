from typing import Any

from app.analysis.text_utils import normalize
from app.schemas.analysis import AnalysisResult
from app.tailoring.providers.base import (
    TailoringContext,
    TailoringProvider,
    TailoringResult,
)


class RuleBasedTailoringProvider(TailoringProvider):
    """Deterministic tailoring engine (MVP, no LLM).

    Only performs safe transformations using information already present:
      - reorder skills so JD-relevant (matched) skills come first
      - reorder experience/projects so entries mentioning JD-relevant terms lead
      - rewrite the summary by prepending matched skills already on the resume
    Never fabricates facts; missing/required-but-absent items surface as
    recommendations/warnings instead of being inserted.
    """
    name = "rule_based"

    def tailor(
        self,
        context: TailoringContext,
        analysis: AnalysisResult,
        job_description: str,
    ) -> TailoringResult:
        relevance = {normalize(t) for t in analysis.matched_keywords}
        relevance |= {normalize(s.name) for s in analysis.matched_skills}
        relevance |= {normalize(k) for k in analysis.job_keywords}
        relevance.discard("")

        changed: list[str] = []
        warnings: list[str] = []

        # ---- skills: matched first, stable otherwise ----
        skills = self._prioritize(
            context.skills,
            key_fn=lambda s: " ".join(str(v) for v in s.values()),
            relevance=relevance,
        )
        if [s.get("name") for s in skills] != [s.get("name") for s in context.skills]:
            changed.append("skills")

        # ---- experience: stable sort by relevance ----
        experience = self._prioritize(
            context.experience,
            key_fn=lambda e: " ".join(
                str(v) for v in (e.get("company"), e.get("title"), e.get("description")) if v
            ),
            relevance=relevance,
        )
        if [e.get("id", e.get("title")) for e in experience] != [
            e.get("id", e.get("title")) for e in context.experience
        ]:
            changed.append("experience")

        # ---- projects: stable sort by relevance ----
        projects = self._prioritize(
            context.projects,
            key_fn=lambda p: " ".join(
                str(v) for v in (p.get("name"), p.get("description")) if v
            ),
            relevance=relevance,
        )
        if [p.get("name") for p in projects] != [p.get("name") for p in context.projects]:
            changed.append("projects")

        # ---- education / certifications: unchanged copies ----
        education = [dict(e) for e in context.education]
        certifications = [dict(e) for e in context.certifications]

        # ---- summary: safe template rewrite using existing matched skills ----
        summary = context.summary
        matched_skill_names = [s.name for s in analysis.matched_skills]
        if summary and matched_skill_names:
            present = [n for n in matched_skill_names if normalize(n) in normalize(summary)]
            missing = [n for n in matched_skill_names if n not in present]
            if missing:
                lead = "Proficient in " + ", ".join(missing) + ". "
                summary = lead + summary
                changed.append("summary")

        # ---- recommendations/warnings for absent items ----
        recommendations: list[str] = []
        if analysis.missing_skills:
            recommendations.append(
                "Consider adding these skills if you have them: "
                + ", ".join(s.name for s in analysis.missing_skills)
                + "."
            )
            warnings.append(
                "Missing skills were NOT added automatically because they are "
                "not present on your resume (no fabrication)."
            )
        if analysis.missing_keywords:
            recommendations.append(
                "Mention where relevant: " + ", ".join(analysis.missing_keywords[:5]) + "."
            )
        if analysis.missing_skills:
            recommendations.extend(analysis.recommendations[:2])

        if not changed:
            warnings.append(
                "No safe deterministic changes were possible for this job description."
            )

        return TailoringResult(
            summary=summary,
            skills=skills,
            experience=experience,
            projects=projects,
            education=education,
            certifications=certifications,
            changed_sections=sorted(set(changed)),
            recommendations=recommendations,
            warnings=warnings,
            provider=self.name,
        )

    @staticmethod
    def _prioritize(entries: list[dict[str, Any]], *, key_fn, relevance: set[str]) -> list[dict[str, Any]]:
        """Stable-sort entries so the most JD-relevant float to the top."""
        def score(entry: dict[str, Any]) -> int:
            text = normalize(key_fn(entry))
            return sum(1 for t in relevance if t and t in text)

        return sorted(entries, key=score, reverse=True)
