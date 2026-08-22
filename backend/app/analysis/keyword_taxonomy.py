"""Important job-description keyword taxonomy (non-skill).

Used to surface meaningful keywords from a job description without echoing
ordinary words. Each keyword is matched at word boundaries. Categories are
kept separate so the analysis can distinguish soft skills, role terms,
tools and domain terms.
"""

KEYWORD_TAXONOMY: dict[str, set[str]] = {
    # Soft skills
    "soft_skill": {
        "communication",
        "teamwork",
        "collaboration",
        "leadership",
        "problem solving",
        "problem-solving",
        "critical thinking",
        "adaptability",
        "ownership",
        "mentoring",
        "stakeholder management",
        "time management",
    },
    # Role / title terms
    "role": {
        "software engineer",
        "full stack",
        "frontend",
        "backend",
        "devops engineer",
        "data scientist",
        "data engineer",
        "product manager",
        "technical lead",
        "architect",
        "senior",
        "staff",
        "intern",
    },
    # Tools / process / platform terms
    "tools": {
        "jira",
        "confluence",
        "slack",
        "grafana",
        "prometheus",
        "vault",
        "helm",
        "serverless",
        "kubernetes",
        "docker",
        "terraform",
        "snowflake",
        "kafka",
    },
    # Domain terms
    "domain": {
        "fintech",
        "e-commerce",
        "healthcare",
        "saas",
        "b2b",
        "b2c",
        "cloud native",
        "distributed systems",
        "high availability",
        "big data",
        "real-time",
        "scalability",
    },
}

SOFTWORDS: set[str] = {
    "and", "the", "of", "to", "for", "with", "a", "an", "in", "on", "at",
    "by", "or", "as", "be", "is", "are", "we", "you", "your", "our",
    "will", "must", "should", "able", "ability", "experience", "skills",
    "strong", "etc", "including", "plus", "job", "role", "team",
}


GENERAL_KEYWORD_CATEGORIES = {"soft_skill", "tools"}
ROLE_DOMAIN_CATEGORIES = {"role", "domain"}


def general_keyword_terms() -> set[str]:
    """Terms used for the general-keyword scoring bucket (soft skills + tools)."""
    out: set[str] = set()
    for cat in GENERAL_KEYWORD_CATEGORIES:
        out.update(KEYWORD_TAXONOMY.get(cat, set()))
    return out


def role_domain_terms() -> set[str]:
    """Terms used for the independent role/domain scoring bucket."""
    out: set[str] = set()
    for cat in ROLE_DOMAIN_CATEGORIES:
        out.update(KEYWORD_TAXONOMY.get(cat, set()))
    return out
