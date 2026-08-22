from typing import Optional

from app.analysis.providers.base import AnalysisProvider, ResumeContext, SkillEntry
from app.analysis.skill_taxonomy import SKILL_TAXONOMY
from app.analysis.keyword_taxonomy import general_keyword_terms, role_domain_terms
from app.analysis.text_utils import find_terms, normalize
from app.schemas.analysis import AnalysisResult, ScoreDetails, SkillMatch


TECHNICAL_WEIGHT = 0.50
KEYWORD_WEIGHT = 0.25
ROLE_DOMAIN_WEIGHT = 0.25


class RuleBasedAnalysisProvider(AnalysisProvider):
    """Deterministic, keyword-based analysis engine (MVP, no LLM).

    Extracts skills and keywords from the job description, compares them
    against the resume content, computes a transparent weighted match score,
    and generates actionable recommendations. Output is deterministic for
    the same inputs, so it is fully testable.

    The score uses three independent term buckets (overall weighting 50/25/25):
      - Technical skills (50%): from SKILL_TAXONOMY
      - General keywords (25%): soft skills + tools (general_keyword_terms)
      - Role/domain (25%): role + domain terms (role_domain_terms)
    """
    name = "rule_based"

    def analyze(self, resume_context: ResumeContext, job_description: str) -> AnalysisResult:
        jd_norm = normalize(job_description)
        resume_all = normalize(resume_context.all_text())
        resume_skill_text = self._resume_skill_text(resume_context)

        jd_skills = self._extract_skills(jd_norm)
        resume_skills = self._extract_skills_from_resume(resume_skill_text, resume_context)
        matched, missing = self._compare_skills(jd_skills, resume_skills)

        # General keywords (soft skills + tools)
        jd_keywords = self._extract_keywords(jd_norm)
        resume_keywords = self._extract_keywords(resume_all)
        matched_kw = sorted(jd_keywords & resume_keywords)
        missing_kw = sorted(jd_keywords - resume_keywords)

        # Independent role/domain terms
        jd_role_domain = self._extract_role_domain(jd_norm)
        resume_role_domain = self._extract_role_domain(resume_all)
        matching_role_domain = jd_role_domain & resume_role_domain

        score_details = self._compute_score(
            matched_skills=matched,
            jd_skills=jd_skills,
            matched_keywords=set(matched_kw),
            jd_keywords=jd_keywords,
            jd_role_domain=jd_role_domain,
            matching_role_domain=matching_role_domain,
        )

        recommendations = self._build_recommendations(
            missing=missing,
            missing_keywords=missing_kw,
            matched_count=len(matched),
            jd_skill_count=len(jd_skills),
            job_keywords=jd_keywords,
        )

        summary = self._build_summary(score_details.overall, len(matched), len(missing))

        all_job_keywords = sorted(jd_keywords | jd_role_domain)
        return AnalysisResult(
            score=score_details.overall,
            score_details=score_details,
            matched_skills=self._to_skill_matches(matched),
            missing_skills=self._to_skill_matches(missing),
            job_keywords=all_job_keywords,
            matched_keywords=matched_kw,
            missing_keywords=missing_kw,
            recommendations=recommendations,
            summary=summary,
            provider=self.name,
        )

    # ---------- extraction ----------

    def _resume_skill_text(self, ctx: ResumeContext) -> str:
        parts = [s.name for s in ctx.skills]
        parts.extend(ctx.experience_descriptions)
        parts.extend(ctx.project_descriptions)
        parts.extend(ctx.summary)
        return "\n".join(p for p in parts if p)

    def _extract_skills(self, text: str) -> set[str]:
        found_aliases = find_terms(text, self._all_aliases())
        return {
            canonical
            for canonical, (_, aliases) in SKILL_TAXONOMY.items()
            if aliases & found_aliases
        }

    def _all_aliases(self) -> set[str]:
        return {a for _, (_, aliases) in SKILL_TAXONOMY.items() for a in aliases}

    def _extract_skills_from_resume(self, text: str, ctx: ResumeContext) -> set[str]:
        canonical = self._extract_skills(text)
        for s in ctx.skills:
            canonical.add(normalize(s.name))
        return canonical

    def _compare_skills(self, jd_skills: set[str], resume_skills: set[str]) -> tuple[list[str], list[str]]:
        matched = sorted(jd_skills & resume_skills)
        missing = sorted(jd_skills - resume_skills)
        return matched, missing

    def _extract_keywords(self, text: str) -> set[str]:
        """General keywords (soft skills + tools) for the keyword bucket."""
        return find_terms(text, general_keyword_terms())

    def _extract_role_domain(self, text: str) -> set[str]:
        """Role/domain terms for the independent role/domain bucket."""
        return find_terms(text, role_domain_terms())

    # ---------- scoring ----------

    def _compute_score(
        self,
        *,
        matched_skills: list[str],
        jd_skills: set[str],
        matched_keywords: set[str],
        jd_keywords: set[str],
        jd_role_domain: set[str],
        matching_role_domain: set[str],
    ) -> ScoreDetails:
        skill_score = (
            round(100.0 * len(matched_skills) / len(jd_skills), 1)
            if jd_skills
            else 0.0
        )
        keyword_score = (
            round(100.0 * len(matched_keywords) / len(jd_keywords), 1)
            if jd_keywords
            else 0.0
        )
        role_domain_score = (
            round(100.0 * len(matching_role_domain) / len(jd_role_domain), 1)
            if jd_role_domain
            else 0.0
        )

        overall = int(
            round(
                TECHNICAL_WEIGHT * skill_score
                + KEYWORD_WEIGHT * keyword_score
                + ROLE_DOMAIN_WEIGHT * role_domain_score
            )
        )
        return ScoreDetails(
            skill_score=skill_score,
            keyword_score=keyword_score,
            role_domain_score=role_domain_score,
            overall=overall,
        )

    # ---------- recommendations / summary ----------

    def _build_recommendations(
        self,
        *,
        missing: list[str],
        missing_keywords: list[str],
        matched_count: int,
        jd_skill_count: int,
        job_keywords: set[str],
    ) -> list[str]:
        recs: list[str] = []
        if missing:
            recs.append(
                "Highlight or gain these skills to better match this role: " + ", ".join(missing) + "."
            )
        if missing_keywords:
            recs.append(
                "Mention these keywords/areas in your resume where relevant: "
                + ", ".join(missing_keywords[:5])
                + "."
            )
        if matched_count == 0 and jd_skill_count > 0:
            recs.append(
                "Your resume currently shows few of the required skills; consider tailoring it to this job description."
            )
        if not recs:
            recs.append(
                "Your resume aligns well with this job description. Continue to emphasise your strongest skills."
            )
        return recs

    def _build_summary(self, overall: int, matched: int, missing: int) -> str:
        if overall >= 75:
            verdict = "strong"
        elif overall >= 50:
            verdict = "moderate"
        else:
            verdict = "weak"
        return (
            f"Overall match is {verdict} ({overall}/100): {matched} required skills matched, "
            f"{missing} missing. Review the recommendations below."
        )

    def _to_skill_matches(self, labels: list[str]) -> list[SkillMatch]:
        return [
            SkillMatch(name=label, category=SKILL_TAXONOMY.get(label, (None, set()))[0])
            for label in labels
        ]
